/**
 * 开局门诊病历 · **界面层的阶段 7 接线**（无头 DOM 桩端到端）。
 *
 * 测的是口径文档 `design/presentation/开局经历疾病接回.md` §十 那四条有没有真的接到屏幕上：
 *   ① 那件事进叙事流；② 候选（≤4）以回应形式钉在底部、认下即落笔（不新开一屏）；
 *   ③ `state.disease` 一有值，纸上诊断栏就由**医师**写上去（玩家只做「认」）；
 *   ④ 「他说话的样子」那一行认了病之后按**病**取。
 *
 * 另外钉三条纪律：界面上没有自由文本入口 · 界面代码里没有新增中文文案字面量（要说的话全在数据里）·
 * 拒答 / 不认病那一局照样能把病历写完并签字（诊断栏仍是空白态）。
 *
 * **不测视觉**（那要看浏览器）；数字键那条路用桩里的 `querySelector` 从渲染出来的 html 读回按钮，
 * 所以「按了数字键」这件事在这里是真按过的。
 */
import { describe, expect, test } from 'bun:test'
import { readFileSync } from 'node:fs'
import db from '../../../data/opening_clinic.json' with { type: 'json' }
import ddb from '../../../data/diseases.json' with { type: 'json' }
import opening from '../../../data/opening.json' with { type: 'json' }
import {
  canSign,
  eventDiseaseCandidates,
  eventOf,
  optionsOf,
  paperColumns,
  plan,
  questionById,
  voiceTally,
} from './opening-clinic.js'

// ── 最小 DOM 桩（照 opening-clinic-flow.test.js 的写法，多两样：
//    `querySelector` 认 `[data-choice-index="N"]`（数字键那条路）· `listeners` 收集 keydown） ──

function makeElement() {
  const el = {
    className: '',
    innerHTML: '',
    textContent: '',
    hidden: false,
    children: [],
    listeners: {},
    append(child) { el.children.push(child) },
    addEventListener(type, fn) { (el.listeners[type] ||= []).push(fn) },
    querySelector() { return null },
    focus() {},
  }
  return el
}

function mountDom() {
  const shell = makeElement()
  const root = makeElement()
  root.querySelector = () => shell
  shell.querySelector = (selector) => {
    const hit = /^\[data-choice-index="(\d)"\]$/.exec(selector)
    if (!hit) return null
    const tag = new RegExp(`<button[^>]*data-choice-index="${hit[1]}"[^>]*>`).exec(shell.innerHTML)
    if (!tag) return null
    const dataset = {}
    for (const attr of tag[0].matchAll(/data-([a-z-]+)="([^"]*)"/g)) {
      dataset[attr[1].replace(/-([a-z])/g, (_, c) => c.toUpperCase())] = attr[2]
    }
    return { dataset }
  }
  const listeners = {}
  globalThis.document = {
    createElement: () => root,
    body: { append() {} },
    documentElement: { classList: { add() {}, remove() {} } },
    addEventListener(type, fn) { (listeners[type] ||= []).push(fn) },
  }
  return { root, shell, listeners }
}

const click = (root, dataset) => {
  const attrs = Object.keys(dataset).map(
    (key) => `[data-${key.replace(/[A-Z]/g, (c) => `-${c.toLowerCase()}`)}]`,
  )
  const target = { closest: (selector) => (attrs.includes(selector) ? { dataset } : null) }
  for (const fn of root.listeners.click ?? []) fn({ target })
}

const pressKey = (listeners, key) => {
  for (const fn of listeners.keydown ?? []) fn({ key, preventDefault() {} })
}

const strip = (html) => html.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ')

/** 纸上那一栏此刻渲染成了什么（从 `data-column` 切到下一栏为止）。 */
function columnHtml(html, id) {
  const at = html.indexOf(`data-column="${id}"`)
  if (at < 0) return ''
  const next = html.indexOf('data-column="', at + 1)
  return html.slice(at, next < 0 ? html.length : next)
}

const map = questionById(db)
const selector = db.questions.find((q) => q.answers === 'complaint')
const wiring = db.event_wiring.ui
const copy = (template, vars = {}) => String(template ?? '').replace(/\{(\w+)\}/g, (_, key) => vars[key] ?? '')

/** 答一局：第一问取指定主诉分支，其余每一问取第一档。 */
function answerAll(root, clinic, branchId) {
  let guard = 0
  while (guard < 200) {
    const state = clinic.state
    const id = plan(db, state.answers).find((x) => state.answers[x] === undefined)
    if (!id) break
    const question = map.get(id)
    const opts = optionsOf(db, question)
    const picked = id === selector.id ? opts.find((o) => o.id === branchId) : opts[0]
    click(root, { answerValue: picked.id })
    if (db.answers[question.answers]?.multi && clinic.state.answers[id] === undefined) {
      click(root, { answerCommit: '1' })
    }
    guard += 1
  }
}

/** 答一局，每一问都答「不愿说」。 */
function refuseAll(root, clinic) {
  let guard = 0
  while (guard < 200) {
    const id = plan(db, clinic.state.answers).find((x) => clinic.state.answers[x] === undefined)
    if (!id) break
    click(root, { answerValue: db.refuse.id })
    guard += 1
  }
}

/** 答一局，能挑到 `voiceId` 那一套的档就挑它；这一问没有那一套就打**没打标**的那一档
 *  （不打 opts[0]——那会把别的调子也数上去，摆不正「他说话的调子」）。 */
function answerAllVoice(root, clinic, voiceId) {
  let guard = 0
  while (guard < 200) {
    const state = clinic.state
    const id = plan(db, state.answers).find((x) => state.answers[x] === undefined)
    if (!id) break
    const question = map.get(id)
    const opts = optionsOf(db, question)
    const picked = opts.find((o) => o.voice === voiceId) ?? opts.find((o) => !o.voice) ?? opts[0]
    click(root, { answerValue: picked.id })
    if (db.answers[question.answers]?.multi && clinic.state.answers[id] === undefined) {
      click(root, { answerCommit: '1' })
    }
    guard += 1
  }
}

async function openClinic() {
  const dom = mountDom()
  const { createOpeningClinic } = await import('./index.js')
  const clinic = createOpeningClinic({ trigger: null, required: true })
  clinic.open()
  return { ...dom, clinic }
}

const diseaseIdsIn = (html) => [...html.matchAll(/data-candidate="([a-z_0-9]+)"/g)].map((m) => m[1])

describe('阶段 7 界面接线：那件事 → 候选 → 认 → 诊断栏', () => {
  test('① 那件事进叙事流：问完了医师那句与院方那句都在流里，写的是数据里的文案', async () => {
    const { root, shell, clinic } = await openClinic()
    expect(shell.innerHTML).not.toContain('data-turn-q="event"')   // 还没问完，不预告
    answerAll(root, clinic, 'sleep')
    const event = eventOf(db, opening, clinic.state)
    expect(event).toBeTruthy()
    expect(shell.innerHTML).toContain('data-turn-q="event"')
    expect(shell.innerHTML).toContain(copy(wiring.event_ask, { title: event.title }))
    expect(shell.innerHTML).toContain(wiring.event_note)
    // 那件事的名字出现在叙事流里（标题来自 data/opening.json 的 events）
    expect(strip(shell.innerHTML)).toContain(event.title)
  })

  test('② 候选 ≤4 钉在底部、带数字键与「认下这一张」；一张候选越不出去', async () => {
    const { root, shell, clinic } = await openClinic()
    answerAll(root, clinic, 'sleep')
    const event = eventOf(db, opening, clinic.state)
    const ids = diseaseIdsIn(shell.innerHTML)
    expect(ids.length).toBeGreaterThan(0)
    expect(ids.length).toBeLessThanOrEqual(4)                       // 上界 = event_rule.candidate_max
    for (const id of ids) expect(event.activates).toContain(id)     // 候选只由那件事的 activates 来
    expect(shell.innerHTML).toContain('data-candidates="1"')
    expect(shell.innerHTML).toContain('data-choice-index="1"')
    expect(shell.innerHTML).toContain(wiring.confirm_action)
    // 候选那一句在数据里的两种说法：收窄到一张用「你说话的样子…」，没收窄用「这几种…」+「还没听出…」
    if (ids.length === 1) {
      const label = ddb.items.find((d) => d.id === ids[0]).label
      expect(shell.innerHTML).toContain(copy(wiring.candidate_narrowed, { label }))
    } else {
      expect(shell.innerHTML).toContain(wiring.candidate_prompt)
      expect(shell.innerHTML).toContain(wiring.candidate_none)
    }
    // 每一张候选都写了它为什么在这儿（「因为你有那件事：…」）
    expect(shell.innerHTML).toContain(copy(wiring.candidate_basis, { title: event.title, label: '' }).slice(0, 12))
  })

  test('③ 认下一张：诊断栏由**医师**落笔写字，profile 里的 diseases 非空', async () => {
    const { root, shell, clinic } = await openClinic()
    const profile = []
    clinic.subscribe((p) => profile.push(p))
    answerAll(root, clinic, 'sleep')
    const id = diseaseIdsIn(shell.innerHTML)[0]
    const label = ddb.items.find((d) => d.id === id).label

    // 还没认之前：纸上诊断栏是**空白态**（那一栏不由玩家落笔，也不许先写）
    const before = columnHtml(shell.innerHTML, 'diagnosis')
    expect(before).toContain(db.record.columns.find((c) => c.id === 'diagnosis').blank)
    expect(before).not.toContain(label)

    click(root, { disease: id })

    const after = columnHtml(shell.innerHTML, 'diagnosis')
    expect(after).toContain(label)                    // 认下了：这一栏有字了
    expect(after).toContain('data-who="hospital"')    // 落笔的是院方
    expect(after).toContain('oc-ink-hospital')        // 院方笔迹
    expect(after).not.toContain(db.record.columns.find((c) => c.id === 'diagnosis').blank)
    // 纸上写了什么，交出去的 profile 就有什么
    expect(clinic.getProfile().diseases).toEqual([id])
    expect(clinic.getProfile().experiences.length).toBeGreaterThan(0)
    expect(clinic.getProfile().clinic.event.id).toBeTruthy()
    expect(clinic.getProfile().clinic.disease).toBe(id)
    // 叙事流里补了一条落笔：医师把它写进了诊断栏
    expect(shell.innerHTML).toContain(copy(wiring.confirmed_note, { label }))
    // 认完即可签字（签字条件没变：问完 + 没签过）
    expect(canSign(db, clinic.state)).toBe(true)
    expect(shell.innerHTML).toContain('data-sign')
    // 签字那一拍广播出去的 profile：经历是那件事的素材、疾病是认下的那张（§10.3 的验收硬标准）
    click(root, { sign: '1' })
    click(root, { confirm: '1' })
    expect(clinic.completed).toBe(true)
    const last = profile[profile.length - 1]
    expect(profile.length).toBeGreaterThan(0)
    expect(last.diseases).toEqual([id])
    expect(last.experiences.length).toBeGreaterThan(0)
    expect(last.clinic.disease).toBe(id)
  })

  test('③ 认下的那一张标出来了；再点同一张 = 反悔，诊断栏退回空白态', async () => {
    const { root, shell, clinic } = await openClinic()
    answerAll(root, clinic, 'sleep')
    const id = diseaseIdsIn(shell.innerHTML)[0]
    click(root, { disease: id })
    expect(shell.innerHTML).toContain('data-confirmed="1"')
    expect(clinic.state.disease).toBe(id)
    click(root, { disease: id })
    expect(clinic.state.disease).toBe(null)
    expect(clinic.getProfile().diseases).toEqual([])
    const column = columnHtml(shell.innerHTML, 'diagnosis')
    expect(column).toContain(db.record.columns.find((c) => c.id === 'diagnosis').blank)
    expect(column).not.toContain('data-confirmed')
  })

  test('③ 数字键也走「认」这一支笔（候选按钮挂在 data-choice-index 上）', async () => {
    const { root, shell, clinic, listeners } = await openClinic()
    answerAll(root, clinic, 'sleep')
    const id = diseaseIdsIn(shell.innerHTML)[0]
    pressKey(listeners, '1')
    expect(clinic.state.disease).toBe(id)
    expect(columnHtml(shell.innerHTML, 'diagnosis')).toContain(ddb.items.find((d) => d.id === id).label)
  })

  test('④ 言语随病：认了病之后那一行按**病**取，不是按这一局的调子', async () => {
    const { root, shell, clinic } = await openClinic()
    answerAll(root, clinic, 'sleep')
    const id = diseaseIdsIn(shell.innerHTML)[0]
    click(root, { disease: id })
    const voice = db.voices.items.find((v) => v.disease === id || (v.covers ?? []).includes(id))
    expect(voice).toBeTruthy()
    expect(shell.innerHTML).toContain(copy(wiring.voice_of_disease, { voice: voice.screen_name }))
    expect(shell.innerHTML).toContain(`data-voice-disease="${id}"`)
  })

  test('精神检查那三行也跟着病走（纸上不另写，由 paperColumns 现算）', async () => {
    const { root, shell, clinic } = await openClinic()
    answerAll(root, clinic, 'sleep')
    const id = diseaseIdsIn(shell.innerHTML)[0]
    const voice = db.voices.items.find((v) => v.disease === id || (v.covers ?? []).includes(id))
    const rows = db.record.observations
      .filter((o) => o.derive?.from === 'voice')
      .map((o) => o.derive.table[voice.id])
      .filter(Boolean)
    expect(rows.length).toBeGreaterThan(0)
    click(root, { disease: id })
    const signs = columnHtml(shell.innerHTML, 'signs')
    for (const text of rows) expect(signs).toContain(text)
    // 契约层那一栏的 derivedFrom 记的是**病**，不是调子
    const columns = paperColumns(db, clinic.state, { character: null, legacyCharacterSource: { identity: {} } })
    const derived = columns.find((c) => c.id === 'signs').rows.map((r) => r.derivedFrom).filter(Boolean)
    expect(derived.every((d) => d.kind === 'disease')).toBe(true)
    expect(derived[0].id).toBe(id)
  })

  test('拒答一局 + 一张病都不认：病历照样写得完、签得下去，诊断栏仍是空白态', async () => {
    const { root, shell, clinic } = await openClinic()
    refuseAll(root, clinic)
    // 一问都没答，也定得下一件事（末条规则是无条件兜底——「恰一件」是结构保证）
    expect(clinic.getProfile().clinic.event.id).toBeTruthy()
    expect(diseaseIdsIn(shell.innerHTML).length).toBeGreaterThan(0)
    expect(shell.innerHTML).toContain('data-sign')
    click(root, { sign: '1' })
    click(root, { confirm: '1' })
    expect(clinic.completed).toBe(true)
    expect(clinic.getProfile().diseases).toEqual([])
    expect(clinic.getProfile().experiences.length).toBeGreaterThan(0)
    const column = paperColumns(db, clinic.state, { character: null, legacyCharacterSource: { identity: {} } })
      .find((c) => c.id === 'diagnosis')
    expect(column.resolved).toBe(false)
    expect(column.text).toBe(db.record.columns.find((c) => c.id === 'diagnosis').blank)
  })

  test('改一改之后再回来：认下的那一张必须仍在候选里，否则退回没认（不许停在自相矛盾的状态）', async () => {
    const { root, shell, clinic } = await openClinic()
    // 先用**往上冲**把一局答完（这一套打标最少，先答它才不会把别的调子顺手数上去）
    const first = 'manic'
    const other = 'depressive'
    answerAllVoice(root, clinic, first)
    expect(voiceTally(db, clinic.state).dominant).toBe(first)
    const confirmed = diseaseIdsIn(shell.innerHTML)[0]
    expect(confirmed).toBeTruthy()
    click(root, { disease: confirmed })
    expect(clinic.state.disease).toBe(confirmed)
    expect(diseaseIdsIn(shell.innerHTML)).toEqual([confirmed])   // 调子显出来了：收窄到 1 张

    // 「落款之前，纸上写的每一句都还能回去改」：回到最早那一处能改的问、改成**沉下去**的说法，
    // 再把剩下的答完 ⇒ 调子倒向另一套 ⇒ 候选收窄到另一张，原来认下的那张已经不在候选里。
    const retag = plan(db, clinic.state.answers)
      .filter((id) => id !== selector.id && clinic.state.answers[id] !== undefined)
      .map((id) => ({ id, option: optionsOf(db, map.get(id)).find((o) => o.voice === other) }))
      .find((x) => x.option)
    expect(retag).toBeTruthy()
    click(root, { reanswer: retag.id })
    answerAllVoice(root, clinic, other)
    expect(voiceTally(db, clinic.state).dominant).toBe(other)

    const candidates = eventDiseaseCandidates(db, opening, ddb, clinic.state).candidates.map((c) => c.id)
    expect(candidates).not.toContain(confirmed)
    expect(clinic.state.disease).toBe(null)
    expect(clinic.getProfile().diseases).toEqual([])
    expect(columnHtml(shell.innerHTML, 'diagnosis')).toContain(db.record.columns.find((c) => c.id === 'diagnosis').blank)
    expect(diseaseIdsIn(shell.innerHTML)).toEqual(candidates)
  })

  test('纪律：界面上没有自由文本入口（三个阶段都核一遍）', async () => {
    const { root, shell, clinic } = await openClinic()
    const needles = ['text' + 'area', 'content' + 'editable', '<' + 'input']
    for (const needle of needles) expect(shell.innerHTML).not.toContain(needle)
    answerAll(root, clinic, 'mood')
    for (const needle of needles) expect(shell.innerHTML).not.toContain(needle)
    click(root, { disease: diseaseIdsIn(shell.innerHTML)[0] })
    for (const needle of needles) expect(shell.innerHTML).not.toContain(needle)
  })

  test('纪律：界面代码里没有新增中文文案字面量（阶段 7 那 11 条都在数据里）', async () => {
    const source = readFileSync(new URL('./index.js', import.meta.url), 'utf8')
    // 去掉注释再搜：注释里引述口径文档是允许的，**代码里**不许写字面量。
    const code = source
      .replace(/\/\*[\s\S]*?\*\//g, '')
      .split('\n')
      .filter((line) => !line.trim().startsWith('//'))
      .join('\n')
    for (const [key, text] of Object.entries(db.event_wiring.ui)) {
      if (key === 'what') continue                     // `what` 是这一块自己的说明，不上屏
      expect({ key, has: code.includes(text) }).toEqual({ key, has: false })
    }
    // 阶段 7 接线里最容易被顺手写死的那几句，逐个再核一遍
    for (const phrase of ['那件事之前', '认下这一张', '诊断栏', '你看哪一个像你自己']) {
      expect({ phrase, has: code.includes(phrase) }).toEqual({ phrase, has: false })
    }
  })
})
