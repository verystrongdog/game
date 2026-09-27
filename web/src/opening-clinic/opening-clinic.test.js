/**
 * 开局门诊病历 · **契约测试**（无状态纯函数那一层）。
 *
 * 测的是判据，不是文案：分支怎么走、答案怎么写进纸里、拒答会不会锁死、校验器认不认得出坏数据。
 * 一切取值都从 `data/opening_clinic.json` 读，测试里**不手抄第二份清单**。
 */
import { describe, expect, test } from 'bun:test'
import { readFileSync, readdirSync } from 'node:fs'
import db from '../../../data/opening_clinic.json' with { type: 'json' }
import ddb from '../../../data/diseases.json' with { type: 'json' }
import odb from '../../../data/opening.json' with { type: 'json' }
import {
  activeColumnId,
  answerLineOf,
  answerSetOf,
  answerTextOf,
  applyAnswer,
  branchSummary,
  canSign,
  chiefComplaint,
  clauseTextOf,
  composeColumn,
  currentQuestion,
  dialogueTurns,
  eventById,
  initialState,
  isMulti,
  isRefuse,
  observationRows,
  optionsOf,
  paperColumns,
  plan,
  profileOf,
  progressOf,
  questionById,
  reAnswer,
  requiredQuestions,
  runCounts,
  sign,
  validateClinic,
  voiceProfiles,
  voiceTally,
} from './opening-clinic.js'

const map = questionById(db)
const selector = db.questions.find((q) => q.answers === 'complaint')
const firstOf = (q) => optionsOf(db, q).find((o) => o.id !== db.refuse.id).id

/** 走一条路：每一步取第 k 档（越界取最后一档），返回终局状态。 */
function walk(branchId, k = 0) {
  let state = { ...initialState(), answers: { [selector.id]: branchId } }
  let guard = 0
  for (;;) {
    const q = currentQuestion(db, state)
    if (!q) break
    if (guard > 300) throw new Error('问诊推进不收敛')
    const opts = optionsOf(db, q)
    const picked = q.id === selector.id ? selector.values?.find?.(() => false) ?? opts.find((o) => o.id === branchId) : opts[Math.min(k, opts.length - 1)]
    const value = isMulti(db, q) ? [picked.id] : picked.id
    state = applyAnswer(db, state, q.id, value).state
    guard += 1
  }
  return state
}

/** 走一条路，但**专挑打了某一套语言指纹的档**（挑不到就走第 k 档）：用来验人格累积与精神检查现算。 */
function walkVoiced(branchId, voiceId, k = 0) {
  let state = { ...initialState(), answers: { [selector.id]: branchId } }
  let guard = 0
  for (;;) {
    const q = currentQuestion(db, state)
    if (!q) break
    if (guard > 300) throw new Error('问诊推进不收敛')
    const opts = optionsOf(db, q)
    const voiced = opts.find((o) => o.voice === voiceId)
    const picked = voiced ?? opts[Math.min(k, opts.length - 1)]
    const value = isMulti(db, q) ? [picked.id] : picked.id
    state = applyAnswer(db, state, q.id, value).state
    guard += 1
  }
  return state
}

describe('题库与参照覆盖面', () => {
  test('参照的 113 问一条都不丢：每一问都有记录，且 ask_mode 在词表里', () => {
    const refs = new Map()
    for (const q of db.questions) refs.set(Math.floor(q.ref), (refs.get(Math.floor(q.ref)) ?? 0) + 1)
    const missing = []
    for (let i = 1; i <= db.meta.owner_reference_total; i += 1) if (!refs.has(i)) missing.push(i)
    expect(missing).toEqual([])
    const modes = new Set(['player', 'observed', 'merged', 'withheld', 'reserved'])
    for (const q of db.questions) expect(modes.has(q.ask_mode)).toBe(true)
  })

  test('每一问都有依据；医方观察与并入/撤回/保留的那几问都写了理由', () => {
    for (const q of db.questions) {
      expect(q.basis).toBeTruthy()
      if (['merged', 'withheld', 'reserved'].includes(q.ask_mode)) expect(q.note).toBeTruthy()
      if (q.ask_mode === 'observed') expect(q.observed_note).toBeTruthy()
    }
  })

  test('必问骨架与题库总数是从数据算出来的，不是写死的', () => {
    expect(db.questions.length).toBeGreaterThanOrEqual(db.meta.owner_reference_total)
    expect(requiredQuestions(db).length).toBeGreaterThan(0)
    for (const q of requiredQuestions(db)) expect(q.ask_mode).toBe('player')
  })
})

describe('答案闭集', () => {
  test('每一问都有闭集，且取值不重复', () => {
    for (const q of db.questions.filter((x) => x.ask_mode === 'player')) {
      const spec = answerSetOf(db, q)
      expect(spec).toBeTruthy()
      expect(spec.values.length).toBeGreaterThanOrEqual(2)
      const ids = spec.values.map((v) => v.id)
      expect(new Set(ids).size).toBe(ids.length)
    }
  })

  test('答案里不出现任何病名（data/diseases.json 的 label）', () => {
    const names = ddb.items.map((d) => d.label).filter(Boolean)
    for (const q of db.questions.filter((x) => x.ask_mode === 'player')) {
      for (const v of answerSetOf(db, q).values) {
        for (const name of names) {
          expect(`${v.label}${v.record ?? ''}`).not.toContain(name)
        }
      }
    }
  })

  test('每一问都带「不愿说」，而且**只带一档**（闭集自带时不再追加全局那一档）', () => {
    expect(db.refuse.id).toBeTruthy()
    expect(db.refuse.policy.sensitive).toBe('required')
    for (const q of db.questions.filter((x) => x.ask_mode === 'player')) {
      const ids = optionsOf(db, q).map((o) => o.id)
      // 「带没带」按 `isRefuse` 判——闭集里自己的那一档（q001 的 decline）与全局的 refuse 是同一个意思。
      expect(ids.filter((id) => isRefuse(db, id)), q.id).toHaveLength(1)
      if (q.sensitive) expect(db.sensitivity_levels[q.sensitive].content_note).toBeTruthy()
    }
  })

  test('对话日志是现算的：只收玩家可答的问，一问一答后面跟着一笔落笔', () => {
    const state = applyAnswer(db, initialState(db), 'q001', ['sleep']).state
    const turns = dialogueTurns(db, state)
    expect(turns.map((t) => t.kind)).toEqual(['doctor', 'patient', 'note'])
    expect(turns[0].text).toBe(questionById(db).get('q001').ask)
    expect(turns[1].text).toBe(answerLineOf(db, questionById(db).get('q001'), ['sleep']))
    // 落笔那一句写的是**纸上的字**（clause），不是患者嘴里的原话（label）
    expect(turns[2].text).toContain(clauseTextOf(db, questionById(db).get('q001'), ['sleep']))
    // 医师的观察（observed）与按安全底线不问的（withheld）都不该出现在对话里
    const asked = new Set(turns.map((t) => t.id))
    for (const q of db.questions) {
      if (q.ask_mode === 'observed' || q.ask_mode === 'withheld') expect(asked.has(q.id)).toBe(false)
    }
  })

  test('敏感问题登记了内容提示语，且提示语里不出现任何具体方式', () => {
    const forbidden = ['刀', '药片', '剂', '绳', '楼', '枪']
    for (const level of Object.values(db.sensitivity_levels)) {
      for (const word of forbidden) expect(level.content_note).not.toContain(word)
    }
  })
})

describe('分支：按主诉走，不平铺', () => {
  test('主诉选择器分出的每一个症状群都真的会多问出题来', () => {
    const branches = branchSummary(db)
    expect(branches.length).toBeGreaterThan(1)
    for (const branch of branches) expect(branch.questions.length).toBeGreaterThan(0)
  })

  test('不选主诉分支时，一局只有必问骨架', () => {
    expect(plan(db, {})).toEqual(requiredQuestions(db).map((q) => q.id))
  })

  test('每一问都在它触发的问之后（顺序按参照编号，分支不会倒挂）', () => {
    for (const q of db.questions) {
      if (!q.trigger) continue
      const target = map.get(q.trigger.q)
      expect(target.ref).toBeLessThan(q.ref)
    }
  })

  test('追问只在触发条件成立时出现，且界面上说得清是为什么', () => {
    const followup = db.questions.find((q) => q.followup && q.trigger?.q === 'q024')
    expect(followup).toBeTruthy()
    expect(followup.trigger.label).toBeTruthy()
    const without = plan(db, { q001: 'sleep', q024: 'no' })
    const with_ = plan(db, { q001: 'sleep', q024: 'many' })
    expect(without).not.toContain(followup.id)
    expect(with_).toContain(followup.id)
  })

  test('一局问数 ≤ 40（含分支与追问）', () => {
    for (const row of runCounts(db)) {
      expect(row.max).toBeLessThanOrEqual(40)
      expect(row.sampled_max).toBeLessThanOrEqual(40)
    }
  })
})

describe('答一句 → 纸上的字', () => {
  test('答案按问的顺序落进它该去的栏目，纸上写的是这一答贡献的那一段（clause）', () => {
    const state = walk('sleep')
    const columns = paperColumns(db, state, { character: null, legacyCharacterSource: { identity: {} } })
    const present = columns.find((c) => c.id === 'present_illness')
    expect(present.rows.length).toBeGreaterThan(3)
    for (const row of present.rows) {
      expect(map.get(row.questionId).column).toBe('present_illness')
      expect(row.text).toBe(clauseTextOf(db, map.get(row.questionId), state.answers[row.questionId]))
    }
  })

  test('病史是整段拼出来的句子：没有「栏目：取值」的填表痕迹，也不照抄患者嘴里的词', () => {
    const state = walk('mood')
    const columns = paperColumns(db, state, { character: null, legacyCharacterSource: { identity: {} } })
    for (const id of ['present_illness', 'past_history', 'personal_history', 'family_history']) {
      const column = columns.find((c) => c.id === id)
      expect(column.composed).toBe(true)
      if (!column.text) continue
      expect(/[：:]/.test(column.text)).toBe(false)
      expect(column.text.endsWith('。')).toBe(true)
      // 患者嘴上那一句（label）与纸上那一句（clause）必须是两份字：纸上不是一行一行照抄对话
      for (const row of column.rows) {
        const spoken = answerLineOf(db, map.get(row.questionId), state.answers[row.questionId])
        if (spoken.length > 6) expect(column.text).not.toContain(spoken)
      }
    }
  })

  test('拒答在纸上留得下痕迹：那一栏里写上未答的是哪几问，而不是把整栏空着', () => {
    let state = { ...initialState(), answers: { q001: 'sleep' } }
    for (;;) {
      const q = currentQuestion(db, state)
      if (!q) break
      const value = isMulti(db, q) ? [db.refuse.id] : db.refuse.id
      state = applyAnswer(db, state, q.id, value).state
    }
    const columns = paperColumns(db, state, { character: null, legacyCharacterSource: { identity: {} } })
    const present = columns.find((c) => c.id === 'present_illness')
    expect(present.unanswered.length).toBeGreaterThan(0)
    expect(present.unanswered.every((u) => u.lead)).toBe(true)
  })

  test('主诉 = 症状 + 持续时间，两半都从答案来', () => {
    const state = walk('sleep')
    const text = chiefComplaint(db, state)
    expect(text).toContain(answerTextOf(db, map.get('q003'), state.answers.q003))
    expect(text).toContain(answerTextOf(db, map.get('q005'), state.answers.q005))
    expect([...text].length).toBeLessThanOrEqual(db.text_limits.chief_complaint_max_chars)
  })

  test('主诉在每一条路径上都拼得出来，且不含阿拉伯数字 / 病名', () => {
    const names = ddb.items.map((d) => d.label).filter(Boolean)
    for (const s of [...db.answers.chief_complaints.values, { id: db.refuse.id, record: db.refuse.record }]) {
      for (const d of [...db.answers.duration.values, { id: db.refuse.id, record: db.refuse.record }]) {
        const text = chiefComplaint(db, { answers: { q003: s.id, q005: d.id }, signed: false })
        expect(text.length).toBeGreaterThan(0)
        expect(/[0-9０-９]/.test(text)).toBe(false)
        for (const name of names) expect(text).not.toContain(name)
      }
    }
  })

  test('精神检查由院方写、玩家只读；能由这一趟问出来的那几行跟着答案落笔', () => {
    const a = paperColumns(db, walkVoiced('mood', 'depressive'), { character: null, legacyCharacterSource: { identity: {} } })
    const b = paperColumns(db, walkVoiced('mood', 'manic'), { character: null, legacyCharacterSource: { identity: {} } })
    const signsA = a.find((c) => c.id === 'signs')
    const signsB = b.find((c) => c.id === 'signs')
    expect(signsA.who).toBe('hospital')
    for (const row of signsA.rows) expect(row.questionId).toBeNull()
    // 六行里至少有一行是按这一趟问出来的东西现算的（说话的调子 / 对应的那一问）
    expect(signsA.rows.some((r) => r.derivedFrom)).toBe(true)
    expect(signsA.rows.map((r) => r.text)).not.toEqual(signsB.rows.map((r) => r.text))
    // 没走到的行仍然有字（回落到这一行自己的写法），不会是空白
    const quiet = paperColumns(db, walk('sleep'), { character: null, legacyCharacterSource: { identity: {} } }).find((c) => c.id === 'signs')
    for (const row of quiet.rows) expect(row.text).toBeTruthy()
  })

  test('两种笔迹分得开：患者侧与院方侧各有自己的墨', () => {
    const columns = paperColumns(db, walk('mood'), { character: null, legacyCharacterSource: { identity: {} } })
    const byId = Object.fromEntries(columns.map((c) => [c.id, c]))
    for (const id of ['present_illness', 'past_history', 'personal_history', 'family_history']) {
      expect(byId[id].who).toBe('patient')
      expect(byId[id].ink).toBe(db.record.ink.patient.id)
    }
    for (const id of ['visit_time', 'department', 'signs', 'auxiliary', 'doctor_sign']) {
      expect(byId[id].who).toBe('hospital')
      expect(byId[id].ink).toBe(db.record.ink.hospital.id)
    }
    expect(byId.signs.rows[0].ink).toBe(db.record.ink.hospital.id)
  })

  // 🔧 阶段 7（2026-09-27）：本条原为「诊断与治疗意见双双留白」。owner 第 6 条裁定推翻了诊断那一半
  // （「玩家认下其中之一，写进诊断栏」），所以按 design/engineering/开局经历疾病接回-设计提示词.md §十
  // 的规定**改成新口径的等价断言**，不是删掉：诊断栏现在由**医师**落笔（derived + hospital），
  // 治疗意见**仍留白**。两条断言一一对应旧断言（fill / resolved / screen_note），只是口径换了。
  test('诊断栏由医师落笔（阶段 7 起不再留白），治疗意见仍留白', () => {
    const columns = paperColumns(db, walk('sleep'), { character: null, legacyCharacterSource: { identity: {} } })
    const diagnosis = columns.find((c) => c.id === 'diagnosis')
    expect(diagnosis.fill).toBe('derived')
    expect(diagnosis.who).toBe('hospital')
    expect(diagnosis.value_from).toBe('confirmed_disease')
    expect(diagnosis.screen_note).toBeTruthy()
    // 没认下病的时候仍然是空白态（纸不会先写一个诊断上去）
    expect(diagnosis.resolved).toBe(false)
    expect(diagnosis.text).toBe(diagnosis.blank)

    const treatment = columns.find((c) => c.id === 'treatment')
    expect(treatment.fill).toBe('blank')
    expect(treatment.resolved).toBe(false)
    expect(treatment.screen_note).toBeTruthy()
  })

  test('纸上没有接不上的笔：每一栏的 fill 都在词表里，且都有空白态', () => {
    const fills = new Set(['hospital', 'patient_input', 'patient_sign', 'derived', 'blank'])
    for (const c of db.record.columns) {
      expect(fills.has(c.fill)).toBe(true)
      expect(c.blank).toBeTruthy()
      expect(c.basis).toBeTruthy()
    }
  })
})

describe('语言指纹：怎么说话，就是病在哪儿现形', () => {
  test('每一套语言指纹都有上屏名、说明与依据；第一版是四套', () => {
    const profiles = voiceProfiles(db)
    expect(profiles.length).toBe(4)
    for (const p of profiles) {
      expect(p.screen_name).toBeTruthy()
      expect(p.screen_note).toBeTruthy()
      expect(p.basis.length).toBeGreaterThan(0)
    }
    expect(new Set(profiles.map((p) => p.id)).size).toBe(profiles.length)
  })

  test('打了语言指纹的档，患者嘴里的那一句与纸上写的字是两份字', () => {
    let voiced = 0
    for (const q of db.questions) {
      if (q.ask_mode !== 'player') continue
      for (const v of answerSetOf(db, q)?.values ?? []) {
        if (!v.voice) continue
        voiced += 1
        expect(v.label).not.toBe(v.clause)
        // 嘴上的那一句里不许出现病名，也不许出现诊断口吻
        for (const name of ddb.items.map((d) => d.label).filter(Boolean)) expect(v.label).not.toContain(name)
      }
    }
    expect(voiced).toBeGreaterThan(20)
  })

  test('人格是挑出来的：同一套语气挑得多，它就成为这一局的调子', () => {
    const profile = voiceProfiles(db)[0]
    const answers = {}
    for (const q of db.questions) {
      if (q.ask_mode !== 'player') continue
      const hit = (answerSetOf(db, q)?.values ?? []).find((v) => v.voice === profile.id)
      if (hit) answers[q.id] = isMulti(db, q) ? [hit.id] : hit.id
    }
    const tally = voiceTally(db, { answers, signed: false })
    expect(tally.dominant).toBe(profile.id)
    expect(tally.counts[profile.id]).toBeGreaterThanOrEqual(db.voices.min_tagged)
  })

  test('话太少时听不出调子：只答一两句不给结论', () => {
    const tally = voiceTally(db, { answers: { q001: 'sleep' }, signed: false })
    expect(tally.dominant).toBeNull()
  })

  test('挑出来的调子决定精神检查里那三行怎么写（同一问、不同调子，行就不同）', () => {
    const table = db.record.observations.find((o) => o.label === '言谈与思维').derive.table
    const texts = Object.keys(table).map((id) => table[id])
    expect(new Set(texts).size).toBe(texts.length)
    const state = { answers: {}, signed: false }
    const rows = observationRows(db, state)
    expect(rows.map((r) => r.label)).toEqual(db.record.observations.map((o) => o.label))
    expect(rows.every((r) => r.text)).toBe(true)
  })
})

describe('拼句：许多档答案整理成一段病史', () => {
  test('四个病史栏目都有拼句模板，每一句都指得回玩家真答过的问', () => {
    for (const id of ['present_illness', 'past_history', 'personal_history', 'family_history']) {
      expect(db.compose[id]).toBeTruthy()
      for (const sentence of db.compose[id].sentences) {
        expect(sentence.basis).toBeTruthy()
        expect(sentence.parts.length).toBeGreaterThan(0)
        for (const part of sentence.parts) {
          expect(map.get(part.q).ask_mode).toBe('player')
        }
      }
    }
  })

  test('没答的那一段整段跳过，不留下半句', () => {
    const composed = composeColumn(db, { answers: {}, signed: false }, 'present_illness')
    expect(composed.text).toBe('')
    expect(composed.sentences).toEqual([])
  })

  test('答了才有字，而且是从头连成句的', () => {
    const state = walk('sleep')
    const composed = composeColumn(db, state, 'present_illness')
    expect(composed.sentences.length).toBeGreaterThan(1)
    expect(composed.text.endsWith('。')).toBe(true)
    // 句子之间是连着的：整段里没有换行、没有「栏目：」的痕迹
    expect(composed.text).not.toContain('\n')
    expect(/[：:]/.test(composed.text)).toBe(false)
  })
})

describe('改一改与回退', () => {
  test('回到某一问重答，跟着它写下的字一起退回去', () => {
    const state = walk('sleep')
    const before = Object.keys(state.answers).length
    const { state: back } = reAnswer(db, state, 'q024')
    expect(Object.keys(back.answers).length).toBeLessThan(before)
    expect(back.answers.q024).toBeUndefined()
    expect(back.answers.q024b).toBeUndefined()
    expect(back.answers.q003).toBeDefined()
  })

  test('换主诉分支会退掉上一个分支写下的字，但主诉那两问不动', () => {
    const state = walk('sleep')
    const { state: next, dropped } = applyAnswer(db, state, 'q001', 'manic')
    expect(dropped).toContain('q023')
    expect(next.answers.q001).toBe('manic')
    expect(next.answers.q003).toBeDefined()
    expect(plan(db, next.answers)).toContain('q054')
  })

  test('界面取不到闭集外的取值', () => {
    const state = initialState()
    const { state: next, rejected } = applyAnswer(db, state, 'q001', '不存在的一档')
    expect(rejected).toBe('value_not_in_closed_set')
    expect(next.answers).toEqual({})
  })

  test('正在填的那一栏跟着问诊条走；问完就落到落款栏', () => {
    const state = initialState()
    expect(activeColumnId(db, state)).toBe(map.get('q001').column)
    expect(activeColumnId(db, walk('sleep'))).toBe('historian_sign')
  })

  test('进度从数据算：答完一局时 index 等于 total', () => {
    const state = walk('sleep')
    const p = progressOf(db, state)
    expect(p.answered).toBe(p.total)
    expect(p.index).toBe(p.total)
  })
})

describe('拒答不锁死（硬判据）', () => {
  test('每一个分支、每一种拒答组合都能把病历写完并签字', () => {
    for (const branch of branchSummary(db)) {
      for (const mode of ['all', 'one']) {
        let state = { ...initialState() }
        let guard = 0
        while (currentQuestion(db, state)) {
          if (guard > 300) throw new Error('不收敛')
          const q = currentQuestion(db, state)
          const opts = optionsOf(db, q)
          const useRefuse = mode === 'all' || q.id === 'q003'
          const value = q.id === selector.id
            ? branch.id
            : useRefuse ? db.refuse.id : opts.find((o) => o.id !== db.refuse.id).id
          state = applyAnswer(db, state, q.id, isMulti(db, q) ? [value] : value).state
          guard += 1
        }
        expect(canSign(db, state)).toBe(true)
        const signed = sign(state)
        expect(signed.signed).toBe(true)
        const paper = paperColumns(db, signed, { character: null, legacyCharacterSource: { identity: {} } })
        expect(paper.find((c) => c.id === 'historian_sign').resolved).toBe(true)
        expect(paper.find((c) => c.id === 'chief_complaint').text).toBeTruthy()
      }
    }
  })

  test('拒答落在纸上的字来自数据（不在代码里另写一份）', () => {
    const state = applyAnswer(db, initialState(), 'q003', db.refuse.id).state
    expect(answerTextOf(db, map.get('q003'), state.answers.q003)).toBe(db.refuse.record)
  })
})

describe('交给运行时的那份东西', () => {
  // 🔧 阶段 7（2026-09-27）：原断言是「两个数组恒为空」——那正是提示词 §六 点名的**洞**
  // （「`experiences: []` · `diseases: []`——两个空数组就是本阶段要填的东西」），而且下游
  // `opening-runtime.js:71` 会拿 `experiences` 去 `settleAttributes`，空数组等于属性恒为 0 且
  // **没有测试兜底**。按 §十 的规定改成新口径的等价断言（仍然钉同一件事：交出去的东西里
  // 经历与疾病是什么），不是删掉。
  test('阶段 7：交出去的经历是那件事的素材、疾病是玩家认下的那张（非空且有据）', () => {
    const p = profileOf(db, walk('sleep'), { character: { source: 'canonical' } })
    const event = p.clinic.event
    expect(event).toBeTruthy()
    expect(event.id).toMatch(/^evt_\d{4}$/)
    // 经历 = 那件事的 source_experiences，且每一条都必须是 data/opening.json 里真实存在的记录
    expect(p.experiences.length).toBeGreaterThan(0)
    const known = new Set(odb.experiences.map((e) => e.id))
    for (const id of p.experiences) expect(known.has(id)).toBe(true)
    expect(p.experiences).toEqual(eventById(odb, event.id).source_experiences)
    // 还没认病时 diseases 是空数组（患者意见栏允许一张都不认）
    expect(p.diseases).toEqual([])
    expect(p.clinic.disease).toBeNull()
    expect(p.clinic.stage).toBe('interview')
  })
})

describe('校验器', () => {
  test('现有数据 0 错', () => {
    const report = validateClinic(db, { diseases: ddb })
    expect(report.errors).toEqual([])
  })

  test('报出来的数字都与数据一致', () => {
    const report = validateClinic(db, { diseases: ddb })
    expect(report.numbers.questions).toBe(db.questions.length)
    expect(report.numbers.required).toBe(requiredQuestions(db).length)
    expect(report.numbers.columns).toBe(db.record.columns.length)
    expect(report.numbers.branches).toBe(branchSummary(db).length)
  })
})

describe('界面层里没有自由文本入口', () => {
  // 判据来自提示词 §一 第 4 条：在这个目录下 grep 三种自由文本入口的标记，命中数必须是 0。
  // 三个探针在测试里拼出来，免得测试自己踩到这条判据。
  test('三种自由文本入口在 web/src/opening-clinic/ 里 0 处', () => {
    const needles = ['text' + 'area', 'content' + 'editable', '<' + 'input']
    const dir = new URL('./', import.meta.url)
    const hits = []
    for (const file of readdirSync(dir).filter((f) => f.endsWith('.js'))) {
      const text = readFileSync(new URL(file, dir), 'utf8')
      for (const needle of needles) if (text.includes(needle)) hits.push(`${file}:${needle}`)
    }
    expect(hits).toEqual([])
  })
})
