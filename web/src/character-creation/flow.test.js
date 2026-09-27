import { afterEach, describe, expect, test } from 'bun:test'
import db from '../../../data/opening.json'
import ddb from '../../../data/diseases.json'
import { interviewPool, interviewQuestions } from './opening.js'
import { complaintText } from './character-source.js'

/**
 * 开局**病历单 + 问诊条**的端到端冒烟测试：从第一问答到落款签字，整条路走一遍。
 *
 * 没有浏览器、没有 jsdom，所以这里给一个最小 DOM 桩：只实现 index.js 真正用到的那几个
 * 接口（createElement / append / innerHTML / addEventListener / querySelector）。
 * 它验证的是「答一句写一行、答完八问看池子、逐条核对、逐条表态、签字」这条路接得上，
 * 以及**改答案会按规则退回条目**；它不验证视觉。
 *
 * 契约数值仍来自 data/opening.json —— 这里不写死任何经历内容。
 */

function makeElement() {
  const el = {
    className: '',
    innerHTML: '',
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

const originalDocument = globalThis.document

function mountDocument() {
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

/**
 * 把一次点击喂给界面。
 * `dataset` 的键就是界面要读的 `data-*` 属性名（驼峰写），例如
 * `{ answerFacet: 'onset', answerValue: 'childhood' }` 会被 `[data-answer-facet]` 认出来。
 */
const click = (root, dataset) => {
  const attrs = Object.keys(dataset).map(
    (key) => `[data-${key.replace(/[A-Z]/g, (c) => `-${c.toLowerCase()}`)}]`,
  )
  const target = { closest: (selector) => (attrs.includes(selector) ? { dataset } : null) }
  for (const fn of root.listeners.click ?? []) fn({ target })
}

/** 按答案对象的顺序把八问答完（多值问逐条点）。 */
function answerAll(root, answers) {
  for (const q of interviewQuestions(db)) {
    const value = answers[q.facet]
    if (value === undefined) continue
    if (Array.isArray(value)) {
      for (const v of value) click(root, { answerFacet: q.facet, answerValue: v })
      if (value.length === 0) click(root, { answerEmpty: q.facet })
    } else {
      click(root, { answerFacet: q.facet, answerValue: value })
    }
  }
}

const ANSWERS = {
  self_report: 'cannot_sleep',
  event: ['threat'],
  context: 'family',
  relation: ['parents'],
  agency: 'coerced',
  onset: 'childhood',
  duration_pattern: 'intermittent',
  duration_span: 'short',
}

const poolOf = (answers) => interviewPool(db, ddb, answers)

/** 把一池里认满十段，返回认下的 id。 */
function confirmTen(root, pool) {
  const ids = []
  for (const id of pool.ids) {
    if (ids.length === db.quota.total) break
    click(root, { entry: id })
    ids.push(id)
  }
  return ids
}

afterEach(() => { globalThis.document = originalDocument })

describe('开局病历单：一问一答 → 核对既往史 → 患者意见 → 落款', () => {
  test('纸上有十栏，最先是患者自述，答完一句纸上就多一行', async () => {
    const { root, shell } = mountDocument()
    const { createCharacterCreation } = await import('./index.js')
    const cc = createCharacterCreation({ trigger: null, required: true })
    cc.open()

    // 纸上按法定栏目顺序排着十栏——一个都不少，顺序也不变。
    const columns = [...shell.innerHTML.matchAll(/data-column="([a-z]+)"/g)].map((m) => m[1])
    expect(columns).toEqual(db.record_shell.paper.required)
    // 主诉与现病史都还没写：显示各自的空白态；问诊条停在第 1 问——患者自述。
    expect(shell.innerHTML).toContain(db.complaint.empty)
    expect(interviewQuestions(db)[0].id).toBe('q_self_report')
    expect(shell.innerHTML).toContain(interviewQuestions(db)[0].ask)

    // 第 1 问：患者自述疾病。纸上写下他自己那一句（主诉那一行还缺时间）。
    const [symptom] = db.complaint.self_report.values
    click(root, { answerFacet: 'self_report', answerValue: symptom.id })
    expect(shell.innerHTML).toContain(symptom.label)
    expect(shell.innerHTML).toContain(interviewQuestions(db)[1].ask)

    // 第 2 问：病历撰写人问病前经历——答案写进「诱因与前驱事件」那一笔，池子跟着换。
    click(root, { answerFacet: 'event', answerValue: 'threat' })
    expect(interviewPool(db, ddb, { self_report: symptom.id, event: ['threat'] }).ids.length)
      .toBeGreaterThanOrEqual(db.quota.total)

    // 时间三问排在经历四问之后（第 6–8 问）。答完起病时间与病程形式，主诉那一行才落成。
    for (const id of ['context', 'relation', 'agency']) {
      click(root, { answerFacet: id, answerValue: ANSWERS[id] })
    }
    expect(shell.innerHTML).toContain(interviewQuestions(db)[5].ask)
    click(root, { answerFacet: 'onset', answerValue: 'childhood' })
    click(root, { answerFacet: 'duration_pattern', answerValue: 'intermittent' })
    expect(shell.innerHTML).toContain(complaintText(db, {
      self_report: symptom.id, onset: 'childhood', duration_pattern: 'intermittent',
    }))

    // 病程形式答成「持续不断」之后，下一问的「瞬时」在按钮上就是灰的（fc_02 在答案侧生效）。
    click(root, { answerFacet: 'duration_pattern', answerValue: 'continuous' })
    expect(shell.innerHTML).toContain('cc-answer blocked')
    // 灰掉的点不动：答了也不写进纸里。
    click(root, { answerFacet: 'duration_span', answerValue: 'instant' })
    expect(shell.innerHTML).not.toContain('一栏 · 瞬时')
    // 可点的照样写得进去，纸上也带上「改一改」。
    click(root, { answerFacet: 'duration_span', answerValue: 'short' })
    expect(shell.innerHTML).toContain('改一改')
  })

  test('答完八问才知道池子；池子里的条目逐条「以上属实」，认满十段才能往下', async () => {
    const { root, shell } = mountDocument()
    const { createCharacterCreation } = await import('./index.js')
    const cc = createCharacterCreation({ trigger: null, required: true })
    cc.open()

    // 没答完时，既往史栏只有空白态，没有一条可点的条目（经历四问答完也还不够：
    // 时间三问排在后面，八问答满才进既往史）。
    answerAll(root, { ...ANSWERS, duration_span: undefined })
    expect(shell.innerHTML).not.toContain('data-entry=')
    expect(shell.innerHTML).toContain(db.interview.screen.pool_note)

    click(root, { answerFacet: 'duration_span', answerValue: ANSWERS.duration_span })
    const pool = poolOf(ANSWERS)
    // 池子里的条目全部上纸，池外的连按钮都没有。
    for (const id of pool.ids) expect(shell.innerHTML).toContain(`data-entry="${id}"`)
    const outsider = db.experiences.find((r) => !pool.ids.includes(r.id)).id
    expect(shell.innerHTML).not.toContain(`data-entry="${outsider}"`)

    // 认下十段：计数跟着走，没满之前「这几条就核到这儿」按不动。
    const confirmed = confirmTen(root, pool)
    expect(confirmed).toHaveLength(db.quota.total)
    expect(cc.getProfile().experiences).toEqual(confirmed)
    expect(shell.innerHTML).toContain(`${db.quota.total}</b> / ${db.quota.total}`)

    click(root, { 'pool-done': '' })
    // 患者意见栏列出候选诊断（这一步是院方写的），表态按钮在纸上。
    const cands = [...shell.innerHTML.matchAll(/data-disease="(dis_\d{4})"/g)].map((m) => m[1])
    expect(cands.length).toBeGreaterThan(0)
    click(root, { disease: cands[0] })
    expect(cc.getProfile().diseases).toEqual([cands[0]])

    // 落款：签字 → completed，profile 就是交给对话运行时的那一份。
    click(root, { stage: 'sign' })
    expect(shell.innerHTML).toContain(db.record_shell.sign.unsigned)
    click(root, { confirm: '' })
    expect(cc.completed).toBe(true)
    const profile = cc.getProfile()
    expect(profile.experiences).toHaveLength(db.quota.total)
    expect(profile.diseases).toEqual([cands[0]])
  })

  test('改答案：换掉池子的那一问会退掉池外的条目，只写病历的那几问不会', async () => {
    const { root, shell } = mountDocument()
    const { createCharacterCreation } = await import('./index.js')
    const cc = createCharacterCreation({ trigger: null, required: true })
    cc.open()

    answerAll(root, ANSWERS)
    const before = poolOf(ANSWERS)
    confirmTen(root, before)
    expect(cc.getProfile().experiences).toHaveLength(db.quota.total)

    // 只写病历的那几问（自述 + 时间三问）：换答案不动池子，十段一条不少。
    click(root, { reanswer: 'q_onset' })
    expect(shell.innerHTML).toContain(db.interview.reanswer_note)
    click(root, { answerFacet: 'onset', answerValue: 'adulthood' })
    expect(cc.getProfile().experiences).toHaveLength(db.quota.total)

    // 参与池子的那一问：换答案换池子，池外的条目必须退回去。
    click(root, { reanswer: 'q_context' })
    click(root, { answerFacet: 'context', answerValue: 'work' })
    const after = poolOf({ ...ANSWERS, onset: 'adulthood', context: 'work' })
    const kept = after.ids.filter((id) => before.ids.includes(id))
    for (const id of cc.getProfile().experiences) expect(after.ids).toContain(id)
    expect(cc.getProfile().experiences.length).toBeLessThanOrEqual(kept.length)
    // 仍在池子里的那些不会被误退。
    for (const id of kept) {
      if (cc.getProfile().experiences.includes(id)) expect(after.ids).toContain(id)
    }
    // 并回到确认阶段：还差几段就得再核几段。
    expect(shell.innerHTML).toContain(db.interview.screen.pool_confirm)
  })

  test('问答条上只有一个「上一问」，纸上的每一笔都能回到那一问重答', async () => {
    const { root, shell } = mountDocument()
    const { createCharacterCreation } = await import('./index.js')
    const cc = createCharacterCreation({ trigger: null, required: true })
    cc.open()

    const qs = interviewQuestions(db)
    click(root, { answerFacet: qs[0].facet, answerValue: ANSWERS[qs[0].facet] })
    click(root, { answerFacet: qs[1].facet, answerValue: ANSWERS[qs[1].facet][0] })
    // 「上一问」退回第 2 问（经历四问的第一问）。
    click(root, { 'ask-back': '' })
    expect(shell.innerHTML).toContain(qs[1].ask)

    // 纸上先前答过的那一笔也带一个「改一改」，点了就回到那一问。
    // （时间三问还没答到，所以拿自述那一笔来试——它在纸上的主诉栏里。）
    click(root, { reanswer: qs[0].id })
    expect(shell.innerHTML).toContain(qs[0].ask)
    expect(cc.getProfile().experiences).toEqual([])
  })

  test('界面里没有自由文本入口，也没有旧五屏的残影', async () => {
    const { root, shell } = mountDocument()
    const { createCharacterCreation } = await import('./index.js')
    const cc = createCharacterCreation({ trigger: null, required: true })
    cc.open()
    answerAll(root, ANSWERS)

    expect(shell.innerHTML).not.toContain('<input')
    expect(shell.innerHTML).not.toContain('<textarea')
    expect(shell.innerHTML).not.toContain('contenteditable')
    expect(shell.innerHTML).not.toContain('锚点')
    for (const gone of ['cc-experience-grid', 'cc-live-summary', 'cc-experience-card',
      'cc-anchor-option', 'cc-category-list', 'cc-disease-grid']) {
      expect(shell.innerHTML, gone).not.toContain(gone)
    }
    // 五屏步条也一起退役：页头里不再有那串栏目按钮（纸上那个 <ol> 是既往史的条目表）。
    const header = shell.innerHTML.match(/<header class="cc-header">[\s\S]*?<\/header>/)[0]
    expect(header).not.toContain('<ol')
    expect(header).not.toContain('<li')
    // 而问诊条确实贴着纸。
    expect(shell.innerHTML).toContain('cc-interview-bar')
  })
})
