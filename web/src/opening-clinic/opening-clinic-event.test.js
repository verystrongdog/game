/**
 * 开局门诊病历 · **阶段 7 契约测试**：那件事 → 病 → 诊断栏。
 *
 * 链条（提示词 §八 的八组职责，逐组至少一条）：
 *   定位 `eventOf` / `seedEvent` · 扩展 `eventExpansions` / `expansionAnswered` ·
 *   候选 `eventDiseaseCandidates` · 认 `confirmDisease` · 落笔 `diagnosisEntry` ·
 *   言语 `voiceOfDisease` / `diseaseVoiceConflict` · 结算 `settleEventAttributes` · 出口 `profileOf`
 *
 * 判据一律从三份权威数据现算（clinic / opening / diseases），测试里**不手抄第二份清单**。
 */
import { describe, expect, test } from 'bun:test'
import db from '../../../data/opening_clinic.json' with { type: 'json' }
import odb from '../../../data/opening.json' with { type: 'json' }
import ddb from '../../../data/diseases.json' with { type: 'json' }
import { settleAttributes } from '../character-creation/opening.js'
import {
  applyAnswer,
  branchSummary,
  candidateBasis,
  confirmDisease,
  confirmedDiseaseId,
  currentQuestion,
  diagnosisEntry,
  diseasesOfVoice,
  diseasesWithoutVoice,
  eventById,
  eventDiseaseCandidates,
  eventExpansionState,
  eventOf,
  eventRuleOf,
  eventsOf,
  expansionAnswered,
  expansionIdOf,
  initialState,
  locateFallbackEventId,
  locateRuleMatches,
  locateRules,
  observationRows,
  optionsOf,
  paperColumns,
  profileOf,
  questionById,
  seedEvent,
  settleEventAttributes,
  validateClinic,
  voiceOfDisease,
  voiceProfiles,
  voiceTally,
} from './opening-clinic.js'

const selector = db.questions.find((q) => q.answers === 'complaint')
const rule = eventRuleOf(odb)

/** 走一条路：每一步取第 k 档（越界取最后一档）。`only` = 只到答完为止。 */
function walk(branchId, k = 0) {
  let state = { ...initialState(), answers: { [selector.id]: branchId } }
  for (let guard = 0; guard < 400; guard += 1) {
    const q = currentQuestion(db, state)
    if (!q) break
    const opts = optionsOf(db, q)
    const picked = q.id === selector.id ? opts.find((o) => o.id === branchId) : opts[Math.min(k, opts.length - 1)]
    state = applyAnswer(db, state, q.id, opts.multi ? [picked.id] : picked.id).state
  }
  return state
}

/** 全部拒答的一局（除了主诉选择器——不选主诉就没有分支）。 */
function walkRefuse(branchId) {
  let state = { ...initialState(), answers: { [selector.id]: branchId } }
  for (let guard = 0; guard < 400; guard += 1) {
    const q = currentQuestion(db, state)
    if (!q) break
    const opts = optionsOf(db, q)
    const picked = q.id === selector.id ? opts.find((o) => o.id === branchId) : opts.find((o) => o.id === db.refuse.id) ?? opts[opts.length - 1]
    state = applyAnswer(db, state, q.id, opts.multi ? [picked.id] : picked.id).state
  }
  return state
}

const cloneOdb = () => JSON.parse(JSON.stringify(odb))
const cloneDb = () => JSON.parse(JSON.stringify(db))
const codes = (brokenDb, brokenOdb) => validateClinic(brokenDb, { diseases: ddb, opening: brokenOdb }).errors.map((e) => e.code)

// ── 定位 ──────────────────────────────────────────────────────────────────

describe('定位：一局恰一件那件事', () => {
  test('规则表有序、每条都有出处、末条是无条件兜底（挑不到任何一条时取 fallback）', () => {
    const rules = locateRules(db)
    expect(rules.length).toBeGreaterThan(0)
    for (const r of rules) {
      expect(r.basis).toBeTruthy()
      expect(r.in.length).toBeGreaterThan(0)
      expect(odb.events.some((e) => e.id === r.event)).toBe(true)
    }
    // 兜底件必须在 events 里，而且**没有任何一条规则的无条件命中**——
    // 所以「空答案集」只能走 fallback，这就是「恰一件」的结构保证。
    const fallbackId = locateFallbackEventId(db)
    expect(odb.events.some((e) => e.id === fallbackId)).toBe(true)
    const none = seedEvent(db, odb, {})
    expect(none.fallback).toBe(true)
    expect(none.id).toBe(fallbackId)
  })

  test('每件事都能被定位到（每条规则各自命中一次 ⇒ 没有任何一件事是死事件）', () => {
    const reached = new Set()
    for (const r of locateRules(db)) {
      const seed = seedEvent(db, odb, { [r.q]: r.in[0] })
      expect(seed.id).toBe(r.event)   // 该条规则之前没有别的规则先命中
      reached.add(seed.id)
    }
    expect(reached.has(locateFallbackEventId(db))).toBe(true)
    expect([...reached].sort()).toEqual(odb.events.map((e) => e.id).sort())
  })

  test('任何已答组合下都定位得到，而且只有一件（one_event_per_run）', () => {
    const seen = new Set()
    for (const branch of branchSummary(db)) {
      const branchQ = plan(db, { [selector.id]: branch.id })
      const maxOpts = Math.max(1, ...branchQ.map((id) => optionsOf(db, questionById(db).get(id)).length))
      for (let k = 0; k < maxOpts; k += 1) {
        const answers = {}
        for (const id of branchQ) {
          const opts = optionsOf(db, questionById(db).get(id))
          if (opts.length) answers[id] = opts[Math.min(k, opts.length - 1)].id
        }
        const seed = seedEvent(db, odb, answers)
        expect(seed.event).toBeTruthy()
        expect(seed.event.id).toMatch(/^evt_\d{4}$/)
        seen.add(seed.id)
      }
    }
    expect(seen.size).toBeGreaterThan(0)
  })

  test('定位是一个函数：同一份答案必得同一件事（不随机、不看顺序）', () => {
    const answers = { q093: 'death', q086: 'cold' }
    expect(eventOf(db, odb, answers).id).toBe(eventOf(db, odb, { ...answers }).id)
  })
})

function plan(database, answers) {
  const ids = []
  const map = questionById(database)
  for (const q of database.questions) {
    if (q.ask_mode !== 'player') continue
    if (!q.trigger) { if (q.id in answers || q.answers === 'complaint') ids.push(q.id); continue }
    const v = answers[q.trigger.q]
    const values = Array.isArray(v) ? v : [v]
    if (v !== undefined && (q.trigger.in ?? []).some((x) => values.includes(x))) ids.push(q.id)
  }
  return ids
}

// ── 事件包：每件事至少一条 ────────────────────────────────────────────────

describe('事件包：每件事都经得起扩展（逐件核）', () => {
  for (const event of odb.events) {
    test(`${event.id}「${event.title}」：扩展位／激活的病／素材／属性效果都对得上`, () => {
      // claim：一句话说清打乱了他人生轨迹的哪一段
      expect(event.claim).toBeTruthy()
      // 扩展位：不少于下限，且覆盖数据点名的四位
      expect(event.expansions.length).toBeGreaterThanOrEqual(rule.expansions_min)
      const axes = new Set(event.expansions.map((x) => x.facet))
      for (const axis of rule.expansion_axes_required) expect(axes.has(axis)).toBe(true)
      // 每一个扩展位都指得回现行题库的一档，而且 label / clause / column 与那一档一致
      for (const x of event.expansions) {
        const q = questionById(db).get(x.q)
        expect(q).toBeTruthy()
        const opt = optionsOf(db, q).find((o) => o.id === x.value_id)
        expect(opt).toBeTruthy()
        expect(x.label).toBe(opt.label)
        expect(x.clause).toBe(opt.clause ?? opt.record ?? opt.label)
        expect(x.column).toBe(q.column)
        expect(odb.vocab[x.facet].values.some((v) => v.id === x.value)).toBe(true)
      }
      // 激活的病：1–4 张、都在名册里、且分属各不相同的语言指纹
      expect(event.activates.length).toBeGreaterThanOrEqual(rule.activates_min)
      expect(event.activates.length).toBeLessThanOrEqual(rule.activates_max)
      const voices = event.activates.map((id) => voiceOfDisease(db, id))
      expect(voices.every(Boolean)).toBe(true)
      expect(new Set(voices.map((v) => v.id)).size).toBe(voices.length)
      // 素材：指得到真记录，且与 activates 相交（「扩写」这件事成立）
      expect(event.source_experiences.length).toBeGreaterThanOrEqual(rule.material_min)
      for (const id of event.source_experiences) {
        const rec = odb.experiences.find((e) => e.id === id)
        expect(rec).toBeTruthy()
        expect(rec.diseases.some((d) => event.activates.includes(d))).toBe(true)
      }
      // 属性效果 = 素材合计（一个数，不是两个）
      const sum = {}
      for (const id of event.source_experiences) {
        const rec = odb.experiences.find((e) => e.id === id)
        for (const [k, v] of Object.entries(rec.effects.attributes)) sum[k] = (sum[k] ?? 0) + v
      }
      expect(event.effects.attributes).toEqual(sum)
      expect(Object.keys(event.effects.attributes).length).toBeLessThanOrEqual(rule.effects_terms_max)
    })
  }
})

// ── 扩展 ──────────────────────────────────────────────────────────────────

describe('扩展位：答了就要上纸', () => {
  test('expansionAnswered 只认「那一档被答出来」，不是「那一问被答了」', () => {
    const event = eventById(odb, 'evt_0001')
    const death = event.expansions.find((x) => x.id === 'q093.death')
    expect(expansionAnswered(db, death, { q093: 'death' })).toBe(true)
    expect(expansionAnswered(db, death, { q093: 'job' })).toBe(false)
    expect(expansionAnswered(db, death, {})).toBe(false)
  })

  test('事件扩展位的每一问都在拼句模板里：答了必写在纸上（expand_not_on_paper 的正例）', () => {
    const composed = new Set(Object.values(db.compose)
      .flatMap((spec) => spec.sentences.flatMap((s) => s.parts.map((p) => p.q))))
    for (const event of odb.events) {
      for (const x of event.expansions) expect(composed.has(x.q)).toBe(true)
    }
  })

  test('已答的扩展位会出现在这一局的纸上（写出来的字里能找到它的临床片段）', () => {
    const state = walk('sleep', 0)
    const event = eventOf(db, odb, state.answers)
    const { answered } = eventExpansionState(db, odb, event, state.answers)
    expect(answered.length).toBeGreaterThan(0)
    const paper = paperColumns(db, state, { character: null, legacyCharacterSource: { identity: {} } })
    const written = paper.filter((c) => c.composed).map((c) => c.text).join('')
    // 至少有一条已答扩展位的片段出现在纸上（否则就是「对话里说了、纸上没写」）
    expect(answered.some((x) => written.includes(x.clause))).toBe(true)
  })
})

// ── 候选与认 ──────────────────────────────────────────────────────────────

describe('候选：≤4，且调子定下来之后收窄到一张', () => {
  test('候选只从那件事的 activates 里来，且不超过上界', () => {
    const state = walk('sleep', 0)
    const { event, candidates, limit } = eventDiseaseCandidates(db, odb, ddb, state)
    expect(candidates.length).toBeGreaterThan(0)
    expect(candidates.length).toBeLessThanOrEqual(limit)
    const acts = new Set(event.activates)
    for (const c of candidates) expect(acts.has(c.id)).toBe(true)
  })

  test('调子显出来 ⇒ 候选恰一张，且与调子一致；调子没显出来 ⇒ 四张里挑', () => {
    let bothSeen = { decided: 0, undecided: 0 }
    for (const branch of branchSummary(db)) {
      for (const k of [0, 1, 2, 3]) {
        const state = walk(branch.id, k)
        const tally = voiceTally(db, state)
        const { candidates } = eventDiseaseCandidates(db, odb, ddb, state)
        if (tally.dominant) {
          bothSeen.decided += 1
          expect(candidates.length).toBe(1)
          expect(voiceOfDisease(db, candidates[0].id).id).toBe(tally.dominant)
        } else {
          bothSeen.undecided += 1
          expect(candidates.length).toBe(4)
        }
      }
    }
    expect(bothSeen.decided).toBeGreaterThan(0)
    expect(bothSeen.undecided).toBeGreaterThan(0)
  })

  test('「因为你有那件事：…」的来源说明带得出那件事与那张病', () => {
    const state = walk('sleep', 0)
    const { candidates } = eventDiseaseCandidates(db, odb, ddb, state)
    const basis = candidateBasis(db, odb, ddb, state, candidates[0].id)
    expect(basis.event).toBe(eventOf(db, odb, state.answers).id)
    expect(basis.title).toBeTruthy()
    expect(basis.disease).toBe(candidates[0].id)
  })

  test('认：正例进得去；反例不在候选里 → not_in_candidates；认完可以反悔', () => {
    const state = walk('sleep', 0)
    const { candidates } = eventDiseaseCandidates(db, odb, ddb, state)
    const good = confirmDisease(db, odb, ddb, state, candidates[0].id)
    expect(good.rejected).toBeNull()
    expect(confirmedDiseaseId(good.state)).toBe(candidates[0].id)
    // 反例：一张名册里存在、但不在本局候选里的病
    const outside = ddb.items.find((d) => d.always_on !== true && !candidates.some((c) => c.id === d.id))
    expect(confirmDisease(db, odb, ddb, state, outside.id).rejected).toBe('not_in_candidates')
    // 反悔
    expect(confirmedDiseaseId(confirmDisease(db, odb, ddb, good.state, null).state)).toBeNull()
  })

  test('反例：认下的病与这一局说话的调子不一致 → voice_disease_conflict（判据必须真的挡得住）', () => {
    // 找一个「调子已经显出来」的局（打标档 ≥ min_tagged）
    let state = null
    let tally = null
    for (const branch of branchSummary(db)) {
      for (const k of [0, 1, 2, 3]) {
        const s = walk(branch.id, k)
        const t = voiceTally(db, s)
        if (t.dominant) { state = s; tally = t; break }
      }
      if (state) break
    }
    expect(state).toBeTruthy()
    // ① 正常数据下，别的指纹代言的病根本进不了候选（先被收窄挡下）
    const otherVoice = voiceProfiles(db).find((v) => v.id !== tally.dominant)
    expect(confirmDisease(db, odb, ddb, state, otherVoice.disease).rejected).toBe('not_in_candidates')
    // ② 数据坏了（那件事只激活一张与调子不符的病）：confirmDisease 必须报 voice_disease_conflict
    const patched = JSON.parse(JSON.stringify(odb))
    const evt = patched.events.find((e) => e.id === eventOf(db, odb, state.answers).id)
    evt.activates = [otherVoice.disease]
    const r = confirmDisease(db, patched, ddb, state, otherVoice.disease)
    expect(r.rejected).toBe('voice_disease_conflict')
    expect(r.conflict.voice).toBe(tally.dominant)
    expect(r.conflict.disease).toBe(otherVoice.disease)
    expect(tally.dominant).not.toBe(otherVoice.id)
    expect(r.conflict.expected.id).toBe(otherVoice.id)   // 这张病该配的是那一套，不是这一局说话的那一套
    expect(r.conflict.reason).toBe('voice_mismatch')
  })
})

// ── 落笔 ──────────────────────────────────────────────────────────────────

describe('诊断栏：医师的笔，玩家只做「认」', () => {
  test('没认病时是空白态，认了之后由医师落笔写病名（ink = 院方）', () => {
    const state = walk('sleep', 0)
    const before = diagnosisEntry(db, odb, ddb, state)
    expect(before.resolved).toBe(false)
    expect(before.text).toBe(db.record.columns.find((c) => c.id === 'diagnosis').blank)
    const { candidates } = eventDiseaseCandidates(db, odb, ddb, state)
    const after = confirmDisease(db, odb, ddb, state, candidates[0].id)
    const entry = diagnosisEntry(db, odb, ddb, after.state)
    expect(entry.resolved).toBe(true)
    expect(entry.text).toBe(ddb.items.find((d) => d.id === candidates[0].id).label)
    expect(entry.ink).toBe(db.record.ink.hospital.id)
  })

  test('纸上那一栏：fill 是 derived、who 是 hospital、value_from 是 confirmed_disease', () => {
    const state = walk('sleep', 0)
    const { candidates } = eventDiseaseCandidates(db, odb, ddb, state)
    const after = confirmDisease(db, odb, ddb, state, candidates[0].id).state
    const paper = paperColumns(db, after, { character: null, legacyCharacterSource: { identity: {} } })
    const diag = paper.find((c) => c.id === 'diagnosis')
    expect(diag.fill).toBe('derived')
    expect(diag.who).toBe('hospital')
    expect(diag.resolved).toBe(true)
    expect(diag.ink).toBe(db.record.ink.hospital.id)
    expect(diag.disease).toBe(candidates[0].id)
    // 治疗意见仍留白（owner 待裁 3 的默认 (a)）
    const tx = paper.find((c) => c.id === 'treatment')
    expect(tx.fill).toBe('blank')
    expect(tx.resolved).toBe(false)
  })
})

// ── 言语 ──────────────────────────────────────────────────────────────────

describe('言语：语言指纹挂在病上', () => {
  test('26 张名册病每一张都有指纹代言，且四套各有一个主病', () => {
    const roster = ddb.items.filter((d) => d.always_on !== true).map((d) => d.id)
    expect(diseasesWithoutVoice(db, roster)).toEqual([])
    const primaries = voiceProfiles(db).map((v) => v.disease)
    expect(primaries.filter(Boolean).length).toBe(voiceProfiles(db).length)
    expect(new Set(primaries).size).toBe(primaries.length)
  })

  test('voiceOfDisease 与 diseasesOfVoice 互逆（主病在前）', () => {
    for (const profile of voiceProfiles(db)) {
      expect(voiceOfDisease(db, profile.disease).id).toBe(profile.id)
      const list = diseasesOfVoice(db, profile.id)
      expect(list[0]).toBe(profile.disease)
      for (const d of list) expect(voiceOfDisease(db, d).id).toBe(profile.id)
    }
  })

  test('认了病之后，精神检查那几行按病取（derivedFrom.kind = disease）', () => {
    const state = walk('sleep', 0)
    const { candidates } = eventDiseaseCandidates(db, odb, ddb, state)
    const after = confirmDisease(db, odb, ddb, state, candidates[0].id).state
    const rows = observationRows(db, after)
    const voiced = rows.filter((r) => r.derivedFrom?.kind === 'disease')
    expect(voiced.length).toBeGreaterThan(0)
    for (const r of voiced) expect(r.derivedFrom.id).toBe(candidates[0].id)
  })
})

// ── 结算 ──────────────────────────────────────────────────────────────────

describe('结算：那件事取代「十段和 = +2」，但只出一个数', () => {
  test('事件的属性效果 ≡ 它那几段素材的结算（两条路径同值，不存在第二份权威）', () => {
    for (const event of odb.events) {
      const mine = settleEventAttributes(odb, event.id)
      const legacy = settleAttributes(odb, [...event.source_experiences])
      expect(mine.raw).toEqual(legacy.raw)
      expect(mine.clamped).toEqual(legacy.clamped)
      expect(mine.totalRaw).toBe(legacy.totalRaw)
      expect(mine.from.materials).toEqual(event.source_experiences)
    }
  })

  test('结算读的是 odb 的 attributes / bands / bounds，不新增字面量', () => {
    const e = settleEventAttributes(odb, odb.events[0].id)
    for (const k of Object.keys(e.raw)) expect(odb.attributes.ids).toContain(k)
    expect(Object.keys(e.band).sort()).toEqual([...odb.attributes.ids].sort())
  })
})

// ── 出口 ──────────────────────────────────────────────────────────────────

describe('出口：profileOf 非空且有据（提示词 §六 的验收硬标准）', () => {
  test('一局走完：experiences = 那件事的素材（都指得到真记录），diseases = 认下的那张', () => {
    const state = walk('sleep', 0)
    const { candidates } = eventDiseaseCandidates(db, odb, ddb, state)
    const after = confirmDisease(db, odb, ddb, state, candidates[0].id).state
    const signed = { ...after, signed: true }
    const profile = profileOf(db, signed, { character: { source: 'canonical' } })
    const event = eventById(odb, profile.clinic.event.id)
    expect(profile.experiences).toEqual(event.source_experiences)
    const known = new Set(odb.experiences.map((e) => e.id))
    for (const id of profile.experiences) expect(known.has(id)).toBe(true)
    expect(profile.diseases).toEqual([candidates[0].id])
    expect(profile.clinic.disease).toBe(candidates[0].id)
    expect(profile.clinic.event.rule).toBeTruthy()
    expect(profile.clinic.event.fallback).toBe(false)
    expect(profile.clinic.event.expansions.length).toBe(eventExpansionState(db, odb, event, signed.answers).answered.length)
  })

  test('一个分支都不例外：每一条路走完，两个数组都非空', () => {
    for (const branch of branchSummary(db)) {
      const state = walk(branch.id, 1)
      const { candidates } = eventDiseaseCandidates(db, odb, ddb, state)
      const after = confirmDisease(db, odb, ddb, state, candidates[0].id).state
      const profile = profileOf(db, { ...after, signed: true })
      expect(profile.experiences.length).toBeGreaterThan(0)
      expect(profile.diseases.length).toBe(1)
    }
  })

  test('下游读得懂：opening-runtime 那条 settleAttributes(db, profile.experiences) 不抛错', () => {
    const state = walk('sleep', 0)
    const profile = profileOf(db, { ...state, signed: true })
    const settlement = settleAttributes(odb, [...profile.experiences])
    expect(settlement.totalRaw).toBeGreaterThan(0)
    expect(Object.keys(settlement.clamped).length).toBe(odb.attributes.ids.length)
  })
})

// ── 拒答 ──────────────────────────────────────────────────────────────────

describe('拒答不锁死：全拒答的一局照样定得出那件事、写得出病历', () => {
  test('全拒答：定位到兜底件，诊断栏不落笔，病历仍以句号收尾', () => {
    const state = walkRefuse('sleep')
    const seed = seedEvent(db, odb, state.answers)
    expect(seed.event).toBeTruthy()
    const paper = paperColumns(db, state, { character: null, legacyCharacterSource: { identity: {} } })
    const diag = paper.find((c) => c.id === 'diagnosis')
    expect(diag.resolved).toBe(false)
    for (const col of paper) {
      if (!col.composed || !col.text) continue
      expect(col.text.endsWith('。')).toBe(true)
    }
    // 认病之后仍然写得出来：候选不是空的，认下即落笔
    const { candidates } = eventDiseaseCandidates(db, odb, ddb, state)
    expect(candidates.length).toBeGreaterThan(0)
    const after = confirmDisease(db, odb, ddb, state, candidates[0].id).state
    expect(diagnosisEntry(db, odb, ddb, after).resolved).toBe(true)
  })

  test('每一个主诉分支的全拒答局都走得完', () => {
    for (const branch of branchSummary(db)) {
      const state = walkRefuse(branch.id)
      expect(seedEvent(db, odb, state.answers).event).toBeTruthy()
      expect(eventDiseaseCandidates(db, odb, ddb, state).candidates.length).toBeGreaterThan(0)
    }
  })
})

// ── 校验层：反例形变 ──────────────────────────────────────────────────────

describe('阶段 7 的判据：数据坏了必须报出来', () => {

  test('正例：未改动的三份数据 0 错', () => {
    expect(codes(cloneDb(), cloneOdb())).toEqual([])
  })

  test('反例：某件事的 activates 掏空 → event_activates_empty', () => {
    const broken = cloneOdb()
    broken.events[0].activates = []
    expect(codes(cloneDb(), broken)).toContain('event_activates_empty')
  })

  test('反例：激活了固有项 dis_0027 → event_activates_always_on', () => {
    const broken = cloneOdb()
    broken.events[0].activates = ['dis_0027']
    expect(codes(cloneDb(), broken)).toContain('event_activates_always_on')
  })

  test('反例：一件事的扩展位砍到 3 个 → event_expansion_thin', () => {
    const broken = cloneOdb()
    broken.events[0].expansions = broken.events[0].expansions.slice(0, 3)
    expect(codes(cloneDb(), broken)).toContain('event_expansion_thin')
  })

  test('反例：扩展位用了 11 facet 之外的轴 → event_facet_unknown', () => {
    const broken = cloneOdb()
    broken.events[0].expansions[0].facet = '心情'
    expect(codes(cloneDb(), broken)).toContain('event_facet_unknown')
  })

  test('反例：扩展位的纸上字与那一档的临床片段不一致 → expansion_clause_mismatch', () => {
    const broken = cloneOdb()
    broken.events[0].expansions[0].clause = '自己编的一句'
    expect(codes(cloneDb(), broken)).toContain('expansion_clause_mismatch')
  })

  test('反例：扩展位指了不存在的问 → expansion_question_unknown', () => {
    const broken = cloneOdb()
    broken.events[0].expansions[0].q = 'q999'
    expect(codes(cloneDb(), broken)).toContain('expansion_question_unknown')
  })

  test('反例：素材悬空 → event_material_dead', () => {
    const broken = cloneOdb()
    broken.events[0].source_experiences = ['exp_9999']
    expect(codes(cloneDb(), broken)).toContain('event_material_dead')
  })

  test('反例：素材与 activates 不相交（扩写关系不成立）→ event_material_not_activating', () => {
    const broken = cloneOdb()
    const evt = broken.events[0]
    const foreign = broken.experiences.find((e) => !e.diseases.some((d) => evt.activates.includes(d)))
    evt.source_experiences = [evt.source_experiences[0], foreign.id]
    expect(codes(cloneDb(), broken)).toContain('event_material_not_activating')
  })

  test('反例：事件的属性效果被手改成别的数 → event_effects_not_from_material', () => {
    const broken = cloneOdb()
    broken.events[0].effects.attributes = { will: 99 }
    expect(codes(cloneDb(), broken)).toContain('event_effects_not_from_material')
  })

  test('反例：一件事没有任何定位规则能到达 → event_unreachable', () => {
    const broken = cloneOdb()
    const brokenDb = cloneDb()
    // 把指向 evt_0008 的那条规则抽掉（它只有一条规则）
    const target = broken.events.find((e) => e.id === 'evt_0008')
    expect(target).toBeTruthy()
    brokenDb.event_wiring.locate.rules = brokenDb.event_wiring.locate.rules.filter((r) => r.event !== 'evt_0008')
    expect(codes(brokenDb, broken)).toContain('event_unreachable')
  })

  test('反例：兜底事件不存在 → event_locate_fallback_missing（「恰一件」就没了结构保证）', () => {
    const brokenDb = cloneDb()
    brokenDb.event_wiring.locate.fallback_event = 'evt_9999'
    expect(codes(brokenDb, cloneOdb())).toContain('event_locate_fallback_missing')
  })

  test('反例：定位规则里的取值不在那一问的闭集里 → locate_value_unknown', () => {
    const brokenDb = cloneDb()
    brokenDb.event_wiring.locate.rules[0].in = ['不存在的档']
    expect(codes(brokenDb, cloneOdb())).toContain('locate_value_unknown')
  })

  test('反例：诊断栏的笔被改回留白 → diagnosis_pen_not_hospital', () => {
    const brokenDb = cloneDb()
    brokenDb.record.columns.find((c) => c.id === 'diagnosis').fill = 'blank'
    expect(codes(brokenDb, cloneOdb())).toContain('diagnosis_pen_not_hospital')
  })

  test('反例：诊断栏标成患者落笔 → diagnosis_pen_not_hospital', () => {
    const brokenDb = cloneDb()
    brokenDb.record.columns.find((c) => c.id === 'diagnosis').who = 'patient'
    expect(codes(brokenDb, cloneOdb())).toContain('diagnosis_pen_not_hospital')
  })

  test('反例：某张被激活的病没人代言 → candidate_without_voice', () => {
    const brokenDb = cloneDb()
    // 把一张被事件激活的病从**所有**指纹的 covers 里删掉（没人代言）
    const activated = new Set(odb.events.flatMap((e) => e.activates))
    let removed = null
    for (const v of brokenDb.voices.items) {
      v.covers = v.covers.filter((id) => {
        if (!removed && activated.has(id) && id !== v.disease) { removed = id; return false }
        return true
      })
    }
    expect(removed).toBeTruthy()
    expect(codes(brokenDb, cloneOdb())).toContain('candidate_without_voice')
  })

  test('反例：一件事的 4 张病挤到同一套指纹里 → event_voice_per_event', () => {
    const brokenOdb = cloneOdb()
    const brokenDb = cloneDb()
    // 把 evt_0001 的 4 张全换成同一套指纹代言的病
    const sameVoice = diseasesOfVoice(brokenDb, brokenDb.voices.items[0].id)
    brokenOdb.events.find((e) => e.id === 'evt_0001').activates = sameVoice.slice(0, 4)
    expect(codes(brokenDb, brokenOdb)).toContain('event_voice_per_event')
  })

  test('反例：事件标题超字数 → event_text_too_long', () => {
    const broken = cloneOdb()
    broken.events[0].title = '一二三四五六七八九十'
    expect(codes(cloneDb(), broken)).toContain('event_text_too_long')
  })

  test('反例：事件文案里塞进时间 facet 的标签 → event_text_leaks_facet_label', () => {
    const broken = cloneOdb()
    const label = odb.vocab[odb.text_lint.from_label_facets[0]].values[0].label
    broken.events[0].summary = `这件事发生得很${label}`
    expect(codes(cloneDb(), broken)).toContain('event_text_leaks_facet_label')
  })

  test('反例：spine 的取值不在 facet 闭集里 → event_spine_value_unknown', () => {
    const broken = cloneOdb()
    broken.events[0].spine.onset = '不存在的档'
    expect(codes(cloneDb(), broken)).toContain('event_spine_value_unknown')
  })

  test('报数：事件数 / 覆盖病数 / 候选分布 / 素材台账都在 numbers 里', () => {
    const report = validateClinic(cloneDb(), { diseases: ddb, opening: cloneOdb() })
    expect(report.numbers.events).toBe(odb.events.length)
    expect(report.numbers.event_diseases_covered).toBe(ddb.items.filter((d) => d.always_on !== true).length)
    expect(report.numbers.roster).toBe(26)
    expect(report.numbers.material.total).toBe(odb.experiences.length)
    expect(report.numbers.material.used + report.numbers.material.unused).toBe(odb.experiences.length)
    expect(report.numbers.voice_mismatch_runs).toBe(0)
    for (const n of Object.keys(report.numbers.candidates)) expect(Number(n)).toBeLessThanOrEqual(4)
  })

  test('那件事的扩展位档数是「正好一条」而不是「一条都没有」', () => {
    for (const event of eventsOf(odb)) {
      expect(event.expansions.length).toBeGreaterThanOrEqual(rule.expansions_min)
      const ids = event.expansions.map(expansionIdOf)
      expect(new Set(ids).size).toBe(ids.length)
    }
  })

  // ── 校准第 2 条：症状闭集不许拿来筛事件（机核，不靠约定）─────────────────

  test('定位规则只问「发生过什么」：每条的 q 都在 experience_questions 白名单里', () => {
    const allow = new Set(db.event_wiring.locate.experience_questions.map((x) => x.q))
    expect(allow.size).toBeGreaterThan(0)
    for (const x of db.event_wiring.locate.experience_questions) expect(x.basis).toBeTruthy()
    for (const r of locateRules(db)) expect(allow.has(r.q)).toBe(true)
  })

  test('正向：本批一条 forbid 级的症状陷阱档都没用（用了就报错）', () => {
    const traps = new Set(db.event_wiring.locate.symptom_traps.filter((t) => t.severity === 'forbid').map((t) => `${t.answer_set}.${t.value_id}`))
    expect(traps.size).toBeGreaterThan(0)
    for (const r of locateRules(db)) {
      const set = questionById(db).get(r.q).answers
      for (const v of r.in) expect(traps.has(`${set}.${v}`)).toBe(false)
    }
  })

  test('反例：拿症状档（chief_complaints.anger）去定位那件事 → locate_uses_symptom_trap', () => {
    const brokenDb = cloneDb()
    // q003 的闭集就是 chief_complaints，`anger`「差点跟人吵起来」是症状
    brokenDb.event_wiring.locate.rules.unshift({ id: 'loc_bad', event: 'evt_0002', q: 'q003', in: ['anger'], basis: '故意写坏' })
    const report = validateClinic(brokenDb, { diseases: ddb, opening: cloneOdb() })
    expect(report.errors.map((e) => e.code)).toContain('locate_uses_symptom_trap')
  })

  test('反例：用白名单之外的问做定位（症状问 q048）→ locate_question_not_experience', () => {
    const brokenDb = cloneDb()
    brokenDb.event_wiring.locate.rules.unshift({ id: 'loc_bad2', event: 'evt_0002', q: 'q048', in: ['always'], basis: '故意写坏' })
    expect(codes(brokenDb, cloneOdb())).toContain('locate_question_not_experience')
  })

  test('正向：本批用了两个「弱判别档」，校验器把它们报成警告而不是悄悄放过', () => {
    const report = validateClinic(cloneDb(), { diseases: ddb, opening: cloneOdb() })
    const weak = report.warnings.filter((w) => w.code === 'locate_uses_weak_discriminator')
    expect(weak.length).toBeGreaterThan(0)
    for (const w of weak) expect(w.detail).toContain('弱判别档')
  })

  // ── 校准第 4 条：不许按 id 跨文件认语义 ──────────────────────────────────

  test('正向：扩展位两端 id 恰好同名时，每一条都写了 same_id_note 说清「同名不是同义」', () => {
    let collisions = 0
    for (const event of odb.events) {
      for (const x of event.expansions) {
        if (x.value_id !== x.value) continue
        collisions += 1
        expect(typeof x.same_id_note).toBe('string')
        expect(x.same_id_note.length).toBeGreaterThan(0)
      }
    }
    expect(collisions).toBeGreaterThan(0)   // 两套数据确实有同名 id，所以要真的核
  })

  test('正向：扩展位的 facet / value 一律取自 opening 的词表，与 clinic 的 value_id 无隐式关系', () => {
    for (const event of odb.events) {
      for (const x of event.expansions) {
        // facet 与 value 都只能在 data/opening.json 的词表里找到
        expect(odb.vocab[x.facet]).toBeTruthy()
        expect(odb.vocab[x.facet].values.some((v) => v.id === x.value)).toBe(true)
        // 而 value_id 只能在 clinic 那一问的闭集里找到——两端各自校验，不互相认
        const q = questionById(db).get(x.q)
        expect(optionsOf(db, q).some((o) => o.id === x.value_id)).toBe(true)
      }
    }
  })

  test('反例：抹掉同名 id 的交代 → expansion_id_collision_unjustified', () => {
    const broken = cloneOdb()
    const target = broken.events.flatMap((e) => e.expansions).find((x) => x.value_id === x.value)
    delete target.same_id_note
    expect(codes(cloneDb(), broken)).toContain('expansion_id_collision_unjustified')
  })

  test('locateRuleMatches 是纯函数：不改 answers、不依赖顺序', () => {
    const answers = { q093: 'death' }
    const snapshot = JSON.stringify(answers)
    expect(locateRuleMatches({ q: 'q093', in: ['death'] }, answers)).toBe(true)
    expect(locateRuleMatches({ q: 'q093', in: ['job'] }, answers)).toBe(false)
    expect(locateRuleMatches({ q: 'q086', in: ['loss'] }, answers)).toBe(false)
    expect(JSON.stringify(answers)).toBe(snapshot)
  })
})
