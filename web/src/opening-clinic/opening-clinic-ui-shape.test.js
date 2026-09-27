/**
 * 开局门诊病历 · **界面形态**（owner 2026-09-27 在真浏览器里看过成品之后的三条裁定）。
 *
 *   ① **纸不随每次点击滚到底**：同一栏里连续落笔位置留住；只有「正在填的那一栏」**换了**才
 *      把它滚进视野（`block: 'nearest'` 的语义，不做平滑动画）；右栏叙事流的滚动改成
 *      **让回应整块进视野**（追加裁定：块 + 24px 装得下 → 滚到刚好带进视野的最小位置；
 *      块比视野还高 → 从块顶往上留 24px 起读；两端夹紧；拿不到尺寸才回落到「滚到最底」）。
 *   ② **右栏只有一个滚动容器**：回应不再是「钉在底部的第二个滚动区」，而是**叙事流末尾的一块**
 *      （`.oc-now`）——整栏只有 `.oc-story` 一个滚动条；`data-responses` / `data-choice-index` /
 *      `data-candidates` / `data-disease` 的语义一个字没变。
 *   ③ **调子色只画在选项上**（左边一条细边 + 调子名那一小块），颜色是**冗余**信息（调子名一直写着）。
 *
 * ⚠️ 这一组测的是**滚动与结构**，不是「好不好看」——真实观感只有真浏览器说了算（见回报里的诚实清单）。
 * 桩里照真浏览器那样建模：`innerHTML` 一换，子元素整套重建、`scrollTop` **归零**；
 * 所以「位置有没有被留住」这件事在桩里是真判过的，不是空转。
 */
import { describe, expect, test } from 'bun:test'
import { readFileSync } from 'node:fs'
import db from '../../../data/opening_clinic.json' with { type: 'json' }
import { activeColumnId, currentQuestion, optionsOf, plan } from './opening-clinic.js'

const cssPath = new URL('./opening-clinic.css', import.meta.url)
const pagePath = new URL('../../../design/presentation/叙事界面原型.html', import.meta.url)
const css = readFileSync(cssPath, 'utf8')
const page = readFileSync(pagePath, 'utf8')
// 结构判据要在**去掉注释**的 CSS 上跑：注释里也会出现 `.oc-now` 这类字眼，
// 不剥掉的话 `[^{]*` 会一路吃到下一个规则的 `{`，把别人的规则体当成它的。
const cssBare = css.replace(/\/\*[\s\S]*?\*\//g, '')

// ── 最小 DOM 桩：多出「那张纸」「叙事流」「正在填的那一栏」三个滚动模型 ──────────────

function makeElement({ onRender = null } = {}) {
  let html = ''
  const el = {
    className: '',
    textContent: '',
    hidden: false,
    children: [],
    listeners: {},
    get innerHTML() { return html },
    // 真浏览器：换 innerHTML = 子元素重建 = scrollTop 归零。
    set innerHTML(value) { html = value; onRender?.(value) },
    append(child) { el.children.push(child) },
    addEventListener(type, fn) { (el.listeners[type] ||= []).push(fn) },
    querySelector() { return null },
    focus() {},
  }
  return el
}

function mountDom() {
  const paper = { scrollTop: 0, scrollHeight: 900, clientHeight: 400 }
  const story = { scrollTop: 0, scrollHeight: 1200, clientHeight: 400 }
  // 回应块（`.oc-now`）在流里的位置与高度：由每条测试自己给场景（装得下 / 装不下）。
  const now = { offsetTop: 0, offsetHeight: 0 }
  const column = { offsetTop: 300, offsetHeight: 200 }
  // 视口矩形：纸容器固定占视野；那一栏随纸往上滚（scrollTop 越大，它在视野里越高）。
  // 生产代码走的就是这条路（`getBoundingClientRect` 的 `block:'nearest'` 语义），所以下面
  // 那几条判据测的是**真跑的那条路**，不是一条备用分支。
  paper.getBoundingClientRect = () => ({ top: 0, bottom: paper.clientHeight })
  column.getBoundingClientRect = () => ({
    top: column.offsetTop - paper.scrollTop,
    bottom: column.offsetTop + column.offsetHeight - paper.scrollTop,
  })
  const shell = makeElement({ onRender: () => { paper.scrollTop = 0; story.scrollTop = 0 } })
  const root = makeElement()
  root.querySelector = () => shell
  shell.querySelector = (selector) => {
    if (selector === '.oc-paper-scroll') return paper
    if (selector === '.oc-story') return story
    if (selector === '.oc-now') return now
    if (selector === '.oc-paper-column-active') return shell.innerHTML.includes('oc-paper-column-active') ? column : null
    return null
  }
  const listeners = {}
  globalThis.document = {
    createElement: () => root,
    body: { append() {} },
    documentElement: { classList: { add() {}, remove() {} } },
    addEventListener(type, fn) { (listeners[type] ||= []).push(fn) },
  }
  return { root, shell, paper, story, now, column, listeners }
}

const click = (root, dataset) => {
  const attrs = Object.keys(dataset).map(
    (key) => `[data-${key.replace(/[A-Z]/g, (c) => `-${c.toLowerCase()}`)}]`,
  )
  const target = { closest: (selector) => (attrs.includes(selector) ? { dataset } : null) }
  for (const fn of root.listeners.click ?? []) fn({ target })
}

async function openClinic() {
  const dom = mountDom()
  const { createOpeningClinic } = await import('./index.js')
  const clinic = createOpeningClinic({ trigger: null, required: true })
  clinic.open()
  return { ...dom, clinic }
}

/** 落一档答案（第一问取指定分支），只为把「正在填的那一栏」推到下一栏去。 */
function answerOne(root, clinic) {
  const pending = currentQuestion(db, clinic.state)
  if (!pending) return null
  const option = optionsOf(db, pending)[0]
  click(root, { answerValue: option.id })
  if (db.answers[pending.answers]?.multi && clinic.state.answers[pending.id] === undefined) {
    click(root, { answerCommit: '1' })
  }
  return pending
}

/** CSS 里某个选择器的规则体（`selectorSource` 是正则源码，`\\.oc-x` 这样传）。 */
const blocksOf = (selectorSource) => [...cssBare.matchAll(new RegExp(`${selectorSource}[^{]*\\{([^}]*)\\}`, 'g'))].map((m) => m[1])

describe('裁定 ①：纸不随每次点击滚到底', () => {
  test('同一栏里连着渲两次，纸的位置留住（不是纸尾）', async () => {
    const { shell, paper, clinic } = await openClinic()
    const columnBefore = activeColumnId(db, clinic.state)
    paper.scrollTop = 120
    clinic.render()
    clinic.render()
    expect(paper.scrollTop).toBe(120)
    expect(paper.scrollTop).not.toBe(paper.scrollHeight)
    expect(activeColumnId(db, clinic.state)).toBe(columnBefore)   // 这一拍确实没换栏
    expect(shell.innerHTML).toContain('class="oc-paper-scroll"')
  })

  test('换栏那一次才把它滚进视野（nearest：那一栏的下沿对齐视野下沿），不是滚到纸尾', async () => {
    const { root, paper, column, clinic } = await openClinic()
    const columnBefore = activeColumnId(db, clinic.state)
    paper.scrollTop = 0                                            // 玩家此刻停在纸头
    answerOne(root, clinic)                                        // 答一句 → 换栏 → 该把新那一栏滚进视野
    expect(activeColumnId(db, clinic.state)).not.toBe(columnBefore)
    expect(paper.scrollTop).toBe(column.offsetTop + column.offsetHeight - paper.clientHeight)
    expect(paper.scrollTop).not.toBe(paper.scrollHeight)
  })

  test('那一栏本来就看得见时，换栏也不动纸（nearest 的另一半）', async () => {
    const { root, paper, column, clinic } = await openClinic()
    // 视野 [100, 500] 正好框住那一栏 [300, 500]：滚进去等于什么都不做。
    paper.scrollTop = 100
    answerOne(root, clinic)
    expect(column.offsetTop).toBeGreaterThanOrEqual(paper.scrollTop)
    expect(column.offsetTop + column.offsetHeight).toBeLessThanOrEqual(paper.scrollTop + paper.clientHeight)
    expect(paper.scrollTop).toBe(100)
  })

  test('叙事流的滚动：让回应整块 + 24px 进视野，不再「永远滚到最底」（追加裁定）', async () => {
    const { story, now, clinic } = await openClinic()
    // 场景：流 1400 高、可视 400；回应块在流里 offsetTop 900、高 200。
    story.scrollHeight = 1400
    story.clientHeight = 400
    now.offsetTop = 900
    now.offsetHeight = 200
    clinic.render()
    // 块 + 24px = 224 ≤ 400 → 滚到「刚好带进视野的最小位置」= 900 + 200 + 24 − 400 = 724
    // （上限是最大滚动量 1400 − 400 = 1000，够）。
    expect(story.scrollTop).toBe(724)
    expect(story.scrollTop).not.toBe(story.scrollHeight)
  })

  test('块比可视高度还高时：从块顶往上留 24px 起读（不是只看见选项下半截）', async () => {
    const { story, now, clinic } = await openClinic()
    story.scrollHeight = 1600
    story.clientHeight = 400
    now.offsetTop = 700
    now.offsetHeight = 600                                   // 600 + 24 > 400 → 走第二条
    clinic.render()
    expect(story.scrollTop).toBe(700 - 24)                   // 676
    expect(story.scrollTop).toBeLessThan(now.offsetTop)       // 块顶在视野里，能从上往下读
  })

  test('两端夹紧：块顶已在视野里时不倒着滚，且不越过最大滚动量', async () => {
    const { story, now, clinic } = await openClinic()
    // 流只有一屏（400 = 400）→ 最大滚动量 0：怎么算都不许滚出负数或超过它。
    story.scrollHeight = 400
    story.clientHeight = 400
    now.offsetTop = 100
    now.offsetHeight = 200
    clinic.render()
    expect(story.scrollTop).toBe(0)
    // 反过来：块远在下面 → 取最大滚动量，而不是算出一个滚不到的位。
    story.scrollHeight = 2000
    story.clientHeight = 400
    now.offsetTop = 1900
    now.offsetHeight = 100
    clinic.render()
    expect(story.scrollTop).toBe(2000 - 400)
  })

  test('拿不到 clientHeight / offsetTop 时才回落到「滚到最底」（不许生产代码走桩没覆盖的路）', async () => {
    const { story, now, clinic } = await openClinic()
    story.scrollHeight = 1200
    story.clientHeight = undefined
    now.offsetTop = 900
    now.offsetHeight = 200
    clinic.render()
    expect(story.scrollTop).toBe(story.scrollHeight)          // 回落：滚到最底
    // offsetTop 拿不到也走同一条退路。
    story.clientHeight = 400
    now.offsetTop = undefined
    clinic.render()
    expect(story.scrollTop).toBe(story.scrollHeight)
  })
})

describe('裁定 ②：右栏只有一个滚动容器', () => {
  test('回应块落在叙事流之内，且没有第二个滚动容器', async () => {
    const { shell } = await openClinic()
    const html = shell.innerHTML
    const storyAt = html.indexOf('class="oc-story"')
    const nowAt = html.indexOf('data-responses="1"')
    expect(storyAt).toBeGreaterThanOrEqual(0)
    expect(nowAt).toBeGreaterThan(storyAt)                       // 同一棵树里，且在流量最后
    expect(html).toContain('class="oc-now"')
    expect(html).not.toContain('class="oc-responses"')           // 旧容器类名不再出现
  })

  test('CSS：`.oc-now` 没有自己的 overflow / max-height；`.oc-responses` 容器类已撤', () => {
    expect(blocksOf('\\.oc-now(?![\\w-])').length).toBeGreaterThan(0)
    for (const body of blocksOf('\\.oc-now(?![\\w-])')) expect(body).not.toMatch(/overflow|max-height/)
    for (const body of blocksOf('\\.oc-responses(?![\\w-])')) expect(body).not.toMatch(/overflow|max-height/)
    // `.oc-responses-label` 只是流里的一个标签，允许留着——但它也不许有滚动。
    for (const body of blocksOf('\\.oc-responses-label')) expect(body).not.toMatch(/overflow|max-height/)
  })

  test('CSS：右栏的滚动区只有 `.oc-story` 一个（纸在世界那一侧，不算）', () => {
    const scrollers = [...new Set([...cssBare.matchAll(/\.(oc-[a-z-]+)[^{]*\{([^}]*)\}/g)]
      .filter(([, , body]) => /overflow(-y)?\s*:\s*(auto|scroll)/.test(body))
      .map(([, name]) => name))]
    expect(scrollers).toContain('oc-story')
    expect(scrollers.filter((s) => s.startsWith('oc-responses') || s === 'oc-now')).toEqual([])
    // 面板的网格行数：说话者条 · 调子条 · 那个唯一的滚动区（以前是四行，第四行是回应区）。
    expect(css).toMatch(/grid-template-rows:\s*auto auto minmax\(0, 1fr\);/)
  })

  test('数字键与候选的语义没变（data-choice-index / data-candidates / data-disease 仍在）', async () => {
    const { root, shell, clinic } = await openClinic()
    expect(shell.innerHTML).toContain('data-choice-index="1"')
    let guard = 0
    while (guard < 200 && currentQuestion(db, clinic.state)) { answerOne(root, clinic); guard += 1 }
    const pending = plan(db, clinic.state.answers).find((id) => clinic.state.answers[id] === undefined)
    expect(pending).toBeUndefined()
    expect(shell.innerHTML).toContain('data-candidates="1"')
    expect(shell.innerHTML).toMatch(/data-disease="[a-z_0-9]+"/)
    // 认下诊断那一拍也挂数字键（跟「答」共用同一套）。
    expect(shell.innerHTML).toMatch(/data-disease="[a-z_0-9]+"[^>]*data-choice-index="1"/)
  })
})

describe('裁定 ③：调子色只画在选项上，且不是唯一线索', () => {
  test('本屏带指纹的档都带色类名，且调子名照旧写着', async () => {
    const { shell } = await openClinic()
    const html = shell.innerHTML
    const toned = [...html.matchAll(/class="oc-choice[^"]*oc-voice-(depressive|manic|paranoid|compulsive)[^"]*"/g)].map((m) => m[1])
    const names = [...html.matchAll(/class="oc-choice-voice">([^<]*)</g)].map((m) => m[1].trim())
    expect(toned.length).toBeGreaterThan(0)
    expect(names.length).toBe(toned.length)                       // 有一个色块就有一个调子名
    for (const name of names) expect(name.length).toBeGreaterThan(0)
    for (const id of new Set(toned)) expect(db.voices.items.some((v) => v.id === id)).toBe(true)
  })

  test('四套颜色都走 CSS 变量、定义在页面 :root 里（与夜色 / 浅底那批同一处）', () => {
    for (const id of ['depressive', 'manic', 'paranoid', 'compulsive']) {
      expect(css).toMatch(new RegExp(`\\.oc-voice-${id}\\b`))
      expect(css).toMatch(new RegExp(`var\\(--voice-${id}\\b`))
      expect(page).toMatch(new RegExp(`--voice-${id}\\s*:`))
    }
  })

  test('颜色不铺整块底色（只画细边与调子名），对比度纪律不破', () => {
    const toneBodies = blocksOf('\\.oc-voice-(?:depressive|manic|paranoid|compulsive)')
    expect(toneBodies.length).toBeGreaterThan(0)
    for (const body of toneBodies) expect(body).not.toMatch(/background/)
    // 选项文字仍然吃 --ink（≥ 4.5:1 的老纪律）；调子名只改 border-color / color。
    expect(css).toMatch(/\.oc-choice-voice\s*\{[^}]*border: 1px solid/)
  })
})
