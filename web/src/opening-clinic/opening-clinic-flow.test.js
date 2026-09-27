/**
 * 开局门诊病历 · **端到端冒烟**：用最小 DOM 桩把界面层跑完一局。
 *
 * 测的是「一张纸 + 贴着纸的问诊条」这个形态走不走得通：开屏 → 一问一答 → 改一改 →
 * 问完 → 落款 → 交出去。**不测视觉**（那要看 `web/scripts/render-clinic.mjs` 与浏览器）。
 */
import { describe, expect, test } from 'bun:test'
import db from '../../../data/opening_clinic.json' with { type: 'json' }
import { branchSummary, clauseTextOf, currentQuestion, dialogueTurns, isRefuse, optionsOf, plan, questionById } from './opening-clinic.js'

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
  globalThis.document = {
    createElement: () => root,
    body: { append() {} },
    documentElement: { classList: { add() {}, remove() {} } },
    addEventListener() {},
  }
  return { root, shell }
}

const click = (root, dataset) => {
  const attrs = Object.keys(dataset).map(
    (key) => `[data-${key.replace(/[A-Z]/g, (c) => `-${c.toLowerCase()}`)}]`,
  )
  const target = { closest: (selector) => (attrs.includes(selector) ? { dataset } : null) }
  for (const fn of root.listeners.click ?? []) fn({ target })
}

const map = questionById(db)
const selector = db.questions.find((q) => q.answers === 'complaint')

/** 答一局：每一问取第一档（多值问取头一档，交给「继续问」提交）。 */
function answerAll(root, clinic, branchId, { skip = [] } = {}) {
  let guard = 0
  for (;;) {
    const state = clinic.state
    const id = plan(db, state.answers).find((x) => state.answers[x] === undefined)
    if (!id || guard > 200) break
    const question = map.get(id)
    if (skip.includes(id)) {
      click(root, { answerValue: db.refuse.id })
      guard += 1
      continue
    }
    const opts = optionsOf(db, question)
    const picked = id === selector.id ? opts.find((o) => o.id === branchId) : opts[0]
    click(root, { answerValue: picked.id })
    if (db.answers[question.answers]?.multi && clinic.state.answers[id] === undefined) {
      click(root, { answerCommit: '1' })
    }
    guard += 1
  }
}

describe('端到端：开始新游戏 → 门诊初诊 → 落款', () => {
  test('开屏就是**游戏里的那一屏**：左边诊室与那张纸 · 右边叙事面板，第一问是主诉', async () => {
    const { root, shell } = mountDom()
    const { createOpeningClinic } = await import('./index.js')
    const clinic = createOpeningClinic({ trigger: null, required: true })
    clinic.open()
    // owner 2026-09-27 阶段 6：不是把现实里的病历表照搬上屏——这一屏就是游戏里的叙事界面（叙事界面布局 §二）。
    expect(shell.innerHTML).toContain('data-pane="world"')          // 左：世界（诊室）
    expect(shell.innerHTML).toContain('data-pane="paper"')          // 桌上那份病历，一直在画面里
    expect(shell.innerHTML).toContain('data-pane="dialogue"')       // 右：叙事面板
    expect(shell.innerHTML).toContain('oc-paper')
    expect(shell.innerHTML).toContain('data-log="1"')
    // 顺序：世界 → 桌上的纸 → 右边的叙事面板（纸在对话之前）
    expect(shell.innerHTML.indexOf('data-pane="world"')).toBeLessThan(shell.innerHTML.indexOf('data-pane="paper"'))
    expect(shell.innerHTML.indexOf('data-pane="paper"')).toBeLessThan(shell.innerHTML.indexOf('data-pane="dialogue"'))
    // 病历不藏在标签页后面：整屏里没有把那张纸藏起来的开关
    expect(shell.innerHTML).not.toContain('<nav class="tabs"')
    // 地点 / 时段 / 状态与世界下沿那句说明都在
    expect(shell.innerHTML).toContain(db.ui.place)
    expect(shell.innerHTML).toContain(db.ui.when)
    expect(shell.innerHTML).toContain(db.ui.world_note)
    // 医师那一句在右侧叙事面板里，现在还是空的
    expect(shell.innerHTML).toContain(db.ui.doctor_tag)
    expect(shell.innerHTML).toContain(map.get('q001').ask)
    expect(shell.innerHTML).toContain('data-column="chief_complaint"')
    // 院方那一栏的六行观察一开始就在纸上（玩家只读），玩家一个字都还没说
    expect(shell.innerHTML).toContain(db.record.observations[0].text)
    expect(shell.innerHTML).toContain(db.record.ink.hospital.label)
    expect(shell.innerHTML).toContain(db.record.ink.patient.label)
    // 回应钉在底部，带数字键提示
    expect(shell.innerHTML).toContain('data-responses="1"')
    expect(shell.innerHTML).toContain('data-choice-index="1"')
  })

  test('答一句：纸上多一段拼好的字，叙事流里多一句落笔；两种笔迹分得开', async () => {
    const { root, shell } = mountDom()
    const { createOpeningClinic } = await import('./index.js')
    const clinic = createOpeningClinic({ trigger: null, required: true })
    clinic.open()
    const opts = optionsOf(db, map.get('q001'))
    click(root, { answerValue: opts[0].id })
    // 能改的地方仍然指得回那一问
    expect(shell.innerHTML).toContain('data-write-from="q001"')
    expect(shell.innerHTML).toContain('oc-ink-patient')
    expect(shell.innerHTML).toContain('oc-ink-hospital')
    // 同一句话也进了叙事面板的**患者那一侧**：对话是形式，纸是产物，两边同步。
    expect(shell.innerHTML).toContain('data-turn="patient"')
    expect(shell.innerHTML).toContain(`data-turn-q="q001"`)
    expect(shell.innerHTML).toContain(db.ui.patient_tag)
    // 医师落笔那一句跟着出现：纸上写的字（clause）不是患者嘴里的原话
    expect(shell.innerHTML).toContain('data-turn="note"')
    expect(shell.innerHTML).toContain(clauseTextOf(db, map.get('q001'), [opts[0].id]))
  })

  test('人格从对话里挑出来：选项挂着说话的调子，患者那一句也带上它', async () => {
    const { root, shell } = mountDom()
    const { createOpeningClinic } = await import('./index.js')
    const clinic = createOpeningClinic({ trigger: null, required: true })
    clinic.open()
    const voiced = optionsOf(db, map.get('q001')).find((o) => o.voice)
    expect(voiced).toBeTruthy()
    const profile = db.voices.items.find((v) => v.id === voiced.voice)
    // 按钮上挂着这一套调子的名字（颜色不是唯一线索）
    expect(shell.innerHTML).toContain(profile.screen_name)
    click(root, { answerValue: voiced.id })
    // 挑过之后，患者那一句上挂着同一枚调子标签，累积计数也跟着走
    expect(dialogueTurns(db, clinic.state).find((t) => t.kind === 'patient').voiceLabel).toBe(profile.screen_name)
    expect(shell.innerHTML).toContain('oc-beat-voice')
    expect(shell.innerHTML).toContain(db.ui.voice_legend)
  })

  test('对话是现算的：改一改之后，那段之后的话一起退回去（没有第二份日志）', async () => {
    const { root, shell } = mountDom()
    const { createOpeningClinic } = await import('./index.js')
    const clinic = createOpeningClinic({ trigger: null, required: true })
    clinic.open()
    const q1 = optionsOf(db, map.get('q001'))
    click(root, { answerValue: q1[0].id })          // 第一问选一个分支
    const second = currentQuestion(db, clinic.state).id
    const q2opts = optionsOf(db, map.get(second))
    click(root, { answerValue: q2opts[0].id })      // 第二问
    const turns = dialogueTurns(db, clinic.state)
    expect(turns.filter((t) => t.kind === 'patient')).toHaveLength(2)
    // 回到第一问重答：第二问答过的话必须从对话里消失（它就是第二份状态会漂的地方）
    click(root, { reanswer: 'q001' })
    const after = dialogueTurns(db, clinic.state).filter((t) => t.kind === 'patient')
    expect(after).toHaveLength(0)
  })

  test('一屏只有一个「不愿说」：闭集自带拒答档时不再追加全局那一档', async () => {
    const { root, shell } = mountDom()
    const { createOpeningClinic } = await import('./index.js')
    const clinic = createOpeningClinic({ trigger: null, required: true })
    clinic.open()
    // q001 的闭集里本来就有 decline（refuse.aliases 的一员）
    const buttons = [...shell.innerHTML.matchAll(/data-answer-value="([a-z_]+)"/g)].map((m) => m[1])
    const refusals = buttons.filter((id) => isRefuse(db, id))
    expect(refusals).toHaveLength(1)
  })

  // 🔧 阶段 7：标题原为「交出去的东西里不结算经历与疾病」，断言两个数组为空——那正是提示词 §六
  // 点名的洞。按 §十 改成新口径的等价断言（同一件事：交出去的东西里经历与疾病是什么），不删。
  test('走完一局：问完 → 落款 → 交出去，交出去的经历与疾病有据（阶段 7）', async () => {
    const { root, shell } = mountDom()
    const { createOpeningClinic } = await import('./index.js')
    const profile = []
    const clinic = createOpeningClinic({ trigger: null, required: true })
    clinic.subscribe((p) => profile.push(p))
    clinic.open()
    answerAll(root, clinic, 'sleep')
    expect(shell.innerHTML).toContain('data-sign')
    click(root, { sign: '1' })
    expect(shell.innerHTML).toContain(db.ui.signed_note)
    expect(shell.innerHTML).toContain('data-confirm')
    click(root, { confirm: '1' })
    expect(clinic.completed).toBe(true)
    const last = profile[profile.length - 1]
    // 那件事定下来了（恰一件），它扩写自的素材 id 跟着交出去；没认病时 diseases 仍为空
    expect(last.clinic.event).toBeTruthy()
    expect(last.experiences.length).toBeGreaterThan(0)
    expect(last.diseases).toEqual([])
    expect(last.clinic.stage).toBe('signed')
  })

  test('敏感问题问之前显示数据里的内容提示，「不愿说」是一个按钮', async () => {
    const { root, shell } = mountDom()
    const { createOpeningClinic } = await import('./index.js')
    const clinic = createOpeningClinic({ trigger: null, required: true })
    clinic.open()
    answerAll(root, clinic, 'sleep', { skip: ['q067'] })
    // 走到 q067 时（跳过的正是它）——直接走到它前面再看一眼
    let guard = 0
    while (clinic.state.answers.q067 === undefined && guard < 200) {
      const id = plan(db, clinic.state.answers).find((x) => clinic.state.answers[x] === undefined)
      if (!id) break
      if (id === 'q067') {
        expect(shell.innerHTML).toContain(db.sensitivity_levels.self_harm.content_note)
        expect(shell.innerHTML).toContain(db.refuse.label)
        break
      }
      const opts = optionsOf(db, map.get(id))
      click(root, { answerValue: id === selector.id ? opts[0].id : opts[0].id })
      if (db.answers[map.get(id).answers]?.multi && clinic.state.answers[id] === undefined) {
        click(root, { answerCommit: '1' })
      }
      guard += 1
    }
    expect(clinic.state.answers.q067).toBe(db.refuse.id)
  })

  test('问出来的追问在界面上说得清是为什么', async () => {
    const { root, shell } = mountDom()
    const { createOpeningClinic } = await import('./index.js')
    const clinic = createOpeningClinic({ trigger: null, required: true })
    clinic.open()
    click(root, { answerValue: db.answers.sleep_onset.values[1].id })
    let guard = 0
    while (clinic.state.answers.q024 === undefined && guard < 200) {
      const id = plan(db, clinic.state.answers).find((x) => clinic.state.answers[x] === undefined)
      if (!id) break
      const opts = optionsOf(db, map.get(id))
      click(root, { answerValue: id === selector.id ? opts[0].id : opts[Math.min(1, opts.length - 1)].id })
      if (db.answers[map.get(id).answers]?.multi && clinic.state.answers[id] === undefined) {
        click(root, { answerCommit: '1' })
      }
      guard += 1
    }
    expect(clinic.state.answers.q024).toBeTruthy()
    if (clinic.state.answers.q024 === 'many' || clinic.state.answers.q024 === 'cant_back') {
      expect(shell.innerHTML).toContain(db.ui.followup_tag)
      expect(shell.innerHTML).toContain(map.get('q024b').trigger.label)
    }
  })

  test('改一改：回到那一问重答，跟着它写下的字一起退回去', async () => {
    const { root, shell } = mountDom()
    const { createOpeningClinic } = await import('./index.js')
    const clinic = createOpeningClinic({ trigger: null, required: true })
    clinic.open()
    answerAll(root, clinic, 'sleep')
    const before = Object.keys(clinic.state.answers).length
    const first = 'q023'
    click(root, { reanswer: first })
    expect(Object.keys(clinic.state.answers).length).toBeLessThan(before)
    expect(clinic.state.answers[first]).toBeUndefined()
    expect(shell.innerHTML).toContain(map.get(first).ask)
  })

  test('整屏里没有自由文本入口，也没有旧 facet 语汇', async () => {
    const { root, shell } = mountDom()
    const { createOpeningClinic } = await import('./index.js')
    const clinic = createOpeningClinic({ trigger: null, required: true })
    clinic.open()
    answerAll(root, clinic, 'mood')
    const html = shell.innerHTML
    for (const needle of ['text' + 'area', 'content' + 'editable', '<' + 'input']) {
      expect(html).not.toContain(needle)
    }
    for (const word of ['在哪', '和谁', '圈内还是圈外', '你能决定多少', 'facet', '锚点']) {
      expect(html).not.toContain(word)
    }
  })

  test('每一个主诉分支都走得完（不许有走不动的分支）', async () => {
    for (const branch of branchSummary(db)) {
      const { root } = mountDom()
      const { createOpeningClinic } = await import('./index.js')
      const clinic = createOpeningClinic({ trigger: null, required: true })
      clinic.open()
      answerAll(root, clinic, branch.id)
      const id = plan(db, clinic.state.answers).find((x) => clinic.state.answers[x] === undefined)
      expect({ branch: branch.id, stuckAt: id }).toEqual({ branch: branch.id, stuckAt: undefined })
    }
  })
})
