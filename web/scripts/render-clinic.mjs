/**
 * 无头形态自检：用最小 DOM 桩把「精神卫生门诊 · 初诊」这一屏渲染出来，打印结构。
 * 没有浏览器时的核对手段（照 `render-cc.mjs` 的写法）。
 *
 *   bun web/scripts/render-clinic.mjs             # 第一问 + 那张纸
 *   bun web/scripts/render-clinic.mjs --all       # 走完一局（每个主诉分支各走一遍）
 *   bun web/scripts/render-clinic.mjs --branch sleep --all
 *   bun web/scripts/render-clinic.mjs --check     # 只做形态自检
 *
 * `--check` 报的九件事（阶段 6 的形态自检 + 阶段 7 的接线与形态裁定）：
 *   ① 自由文本 0（`web/src/opening-clinic/` 里 `textarea` / `contenteditable` / `<input` = 0 处）
 *   ② 旧 facet 语汇 0（「在哪 / 和谁 / 圈内还是圈外 / 你能决定多少」这类分类轴语言）
 *   ③ 栏目序列（第十三条的法定顺序）
 *   ④ 世界（诊室）· 桌上那张纸（一直在画面里）· 叙事面板 · 对话日志在不在
 *   ⑤ 病史是不是**整合成句**：拼出来的四栏里没有「栏目：取值」的冒号痕迹
 *   ⑥ 语言指纹：四套在不在、打了标的档有多少、走完一局之后这一局落在哪一套
 *   ⑦ 阶段 7：那件事 → 病 → 诊断栏（事件包 / 覆盖病 / 候选分布 / 素材台账）
 *   ⑧ 阶段 7 的**界面接线**：那件事进叙事流 · 候选排在流的末尾 · 认下即由医师落笔 · 言语随病
 *      （真点一遍一局，读渲染出来的 html；缺一项就非零退出）
 *   ⑨ owner 2026-09-27 看过成品之后的三条**形态裁定**：① 纸不随每次点击滚到底（只有换栏才滚一次）；
 *      ② 右栏只有一个滚动容器（回应是叙事流末尾的一块）；③ 调子色只画在选项上、且调子名照旧写着；
 *      ④ **追加**：叙事流的滚动 = 让回应整块进视野（装得下 → 刚好带进视野的最小位置；装不下 → 从块顶
 *         往上留 24px 起读；两端夹紧；拿不到尺寸才回落到滚到最底）——两条分支各一条判据。
 * 它验证的是「**这一屏就是游戏里的那一屏**（左世界含那张纸 · 右叙事流）」这个形态本身，不验证视觉。
 */
import { readFileSync, readdirSync } from 'node:fs'
import db from '../../data/opening_clinic.json' with { type: 'json' }
import openingJson from '../../data/opening.json' with { type: 'json' }
import {
  activeColumnId,
  applyAnswer,
  branchSummary,
  currentQuestion,
  eventOf,
  optionsOf,
  paperColumns,
  plan,
  questionById,
  refuseIds,
  validateClinic,
  voiceTally,
} from '../src/opening-clinic/opening-clinic.js'
import ddb from '../../data/diseases.json' with { type: 'json' }

function makeElement({ onRender = null } = {}) {
  let html = ''
  const el = {
    className: '',
    textContent: '',
    hidden: false,
    children: [],
    listeners: {},
    get innerHTML() { return html },
    // 真浏览器里 `innerHTML = …` 会把子元素整套换掉——**滚动位置随之归零**（新元素 scrollTop = 0）。
    // 桩照这个模型做（`onRender` 就是「换了一套子元素」那一拍），否则裁定 ① 那条判据是空的。
    set innerHTML(value) { html = value; onRender?.(value) },
    append(child) { el.children.push(child) },
    addEventListener(type, fn) { (el.listeners[type] ||= []).push(fn) },
    querySelector() { return null },
    focus() {},
  }
  return el
}

function mountDocument() {
  // 那张纸与叙事流的滚动模型（裁定 ①②④ 的判据要用）：纸比视野高，当前那一栏在纸的中间。
  const paper = { scrollTop: 0, scrollHeight: 900, clientHeight: 400 }
  const story = { scrollTop: 0, scrollHeight: 1200, clientHeight: 400 }
  const now = { offsetTop: 0, offsetHeight: 0 }   // 回应块在流里的位置与高度（④ 的场景逐个给）
  const column = { offsetTop: 300, offsetHeight: 200 }
  // 视口矩形：生产代码走的就是这条路（`getBoundingClientRect` 的 `block:'nearest'` 语义），
  // 所以 ⑨ 那条判据测的是**真跑的那条路**，不是一条备用分支。
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
  globalThis.document = {
    createElement: () => root,
    body: { append() {} },
    documentElement: { classList: { add() {}, remove() {} } },
    addEventListener() {},
  }
  return { root, shell, paper, story, now, column }
}

const click = (root, dataset) => {
  const attrs = Object.keys(dataset).map(
    (key) => `[data-${key.replace(/[A-Z]/g, (c) => `-${c.toLowerCase()}`)}]`,
  )
  const target = { closest: (selector) => (attrs.includes(selector) ? { dataset } : null) }
  for (const fn of root.listeners.click ?? []) fn({ target })
}

const strip = (html) => html
  .replace(/<[^>]+>/g, '\n')
  .split('\n')
  .map((x) => x.trim())
  .filter(Boolean)

const sections = (html) => [...html.matchAll(/data-column="([a-z_]+)"/g)].map((m) => m[1])

const args = process.argv.slice(2)
const flag = (name) => {
  const at = args.indexOf(name)
  return at >= 0 ? (args[at + 1] ?? true) : null
}
const has = (name) => args.includes(name)

const moduleDir = new URL('../src/opening-clinic/', import.meta.url)

if (has('--check')) {
  const files = readdirSync(moduleDir).filter((f) => f.endsWith('.js'))
  const sources = files.map((f) => [f, readFileSync(new URL(f, moduleDir), 'utf8')])

  // ① 自由文本：代码里 0 处
  const freeTextHits = []
  for (const [file, text] of sources) {
    for (const needle of ['textarea', 'contenteditable', '<input']) {
      const count = text.split(needle).length - 1
      if (count) freeTextHits.push(`${file} × ${count}（${needle}）`)
    }
  }
  console.log('自由文本入口（textarea / contenteditable / <input>）：', freeTextHits.length ? freeTextHits.join(' · ') : '0 处')

  // ② 旧 facet 语汇：只在**上屏文案**里搜（依据表与注释允许出现这些词，它们不上屏）
  const facetWords = ['在哪', '和谁', '圈内还是圈外', '你能决定多少', 'facet', '锚点', '字段', '维度', '池子', '配额', 'selector', '找池子']
  const onScreenCopy = [
    ...Object.values(db.ui),
    ...db.questions.flatMap((q) => [q.ask, q.lead, q.trigger?.label]),
    ...db.questions.flatMap((q) => (q.answers ? db.answers[q.answers].values.flatMap((v) => [v.label, v.record]) : [])),
    ...db.record.observations.flatMap((o) => [o.label, o.text]),
    ...db.record.columns.flatMap((c) => [c.label, c.blank]),
  ].filter(Boolean)
  const facetHits = [...new Set(onScreenCopy.filter((s) => facetWords.some((w) => String(s).includes(w))))]
  console.log('上屏文案里的旧 facet 语汇：', facetHits.length ? facetHits.join(' · ') : '0 处')

  // 桩里的滚动模型：`paperScroll` 是那张纸，`paperColumn` 是「正在填的那一栏」。
  const { root, shell, paper: paperScroll, column: paperColumn, story: storyScroll, now: nowBlock } = mountDocument()
  const { createOpeningClinic } = await import('../src/opening-clinic/index.js')
  const clinic = createOpeningClinic({ trigger: null, required: true })
  clinic.open()
  const map0 = questionById(db)

  // 上屏文案里不许漏内部词
  const onScreen = strip(shell.innerHTML).join(' ')
  const leak = facetWords.filter((w) => onScreen.includes(w))
  console.log('上屏文案漏内部词：', leak.length ? leak.join(' · ') : '（无）')

  // ③ 栏目序列（法定顺序）
  const paper = paperColumns(db, { answers: {}, signed: false }, { character: null, legacyCharacterSource: { identity: {} } })
  console.log('栏目序列（首页）：', paper.filter((c) => c.group === 'homepage').map((c) => c.label).join(' → '))
  console.log('栏目序列（病历）：', paper.filter((c) => c.group === 'body').map((c) => c.label).join(' → '))

  // ④ 世界 · 桌上那张纸 · 叙事面板 · 对话日志
  const refuses = refuseIds(db)
  const html = shell.innerHTML
  console.log('世界（诊室）：', /data-pane="world"/.test(html) ? '在' : '不在')
  console.log('桌上那张纸（一直在画面里）：', /data-pane="paper"/.test(html) ? '在' : '不在')
  console.log('叙事面板（右栏）：', /data-pane="dialogue"/.test(html) ? '在' : '不在')
  console.log('对话日志：', /data-log="1"/.test(html) ? '在' : '不在')
  console.log('回应接着排在叙事流末尾（数字键）：', /data-responses="1"/.test(html) && /data-choice-index="1"/.test(html) ? '在' : '不在')
  const refusals = [...html.matchAll(/data-answer-value="([a-z_]+)"/g)].map((m) => m[1]).filter((id) => refuses.has(id))
  console.log('「不愿说」档数：', refusals.length, '（同一屏只该有一档）')
  console.log('纸上正在填的那一栏：', sections(shell.innerHTML).length ? '高亮机制在（data-column）' : '不在')

  // ⑤ 病史是不是整合成句：走完一局，四栏拼出来的字里不许有「栏目：取值」的冒号痕迹
  {
    const selector = db.questions.find((q) => q.answers === 'complaint')
    let state = clinic.state
    state.answers = { [selector.id]: 'sleep' }
    state.signed = false
    let guard = 0
    while (guard < 200) {
      const id = plan(db, state.answers).find((x) => state.answers[x] === undefined)
      if (!id) break
      const both = optionsOf(db, map0.get(id))
      const picked = both[Math.min(both.length - 1, 0)]
      const applied = applyAnswer(db, state, id, picked.id)
      state.answers = applied.state.answers
      guard += 1
      state = applied.state
    }
    const columns = paperColumns(db, state, { character: null, legacyCharacterSource: { identity: {} } })
    const prose = columns.filter((c) => c.composed)
    const bad = prose.filter((c) => c.text && (/[：:]/.test(c.text) || !c.text.endsWith('。')))
    console.log('病史整合成句：', prose.length, '栏 ·', prose.reduce((n, c) => n + c.sentences.length, 0), '句 ·', bad.length ? `有填表痕迹：${bad.map((c) => c.label).join('、')}` : '没有「栏目：取值」的痕迹')
    console.log('一局之后的调子：', voiceTally(db, state).dominantLabel ?? '还听不出')
  }

  // ⑥ 语言指纹
  const voicedValues = db.questions.reduce((sum, q) => (q.ask_mode === 'player'
    ? sum + (q.answers ? db.answers[q.answers].values.filter((v) => v.voice).length : 0) : sum), 0)
  console.log('语言指纹：', db.voices.items.map((v) => `${v.screen_name}（${v.id}）`).join(' · '), '· 打了标的档', voicedValues, '档 · 阈值', db.voices.min_tagged)

  const report = validateClinic(db, { diseases: ddb })
  console.log('契约校验：', report.errors.length, '错 /', report.warnings.length, '警告')
  console.log('题库：', report.numbers.questions, '条 · 必问骨架', report.numbers.required, '问 · 栏目', report.numbers.columns, '栏')
  console.log('一局问数：')
  for (const row of report.numbers.runs) {
    console.log(`  ${row.label}：分支 ${row.branch_questions} 问 · 一局 ${row.min}–${row.max} 问（中位 ${row.median}）· 采样最长 ${row.sampled_max}`)
  }

  // ⑦ 阶段 7：那件事 → 病 → 诊断栏（提示词 §十一 点名要的那一组数）
  const n = report.numbers
  const expSizes = n.event_expansions.map((e) => e.expansions).sort((a, b) => a - b)
  const median = expSizes.length % 2
    ? expSizes[(expSizes.length - 1) / 2]
    : (expSizes[expSizes.length / 2 - 1] + expSizes[expSizes.length / 2]) / 2
  console.log('那件事（阶段 7）：', n.events, '件事 · 覆盖', n.event_diseases_covered, '/', n.roster, '张名册病')
  console.log('  每件事扩展位：', expSizes[0], '/', median, '/', expSizes[expSizes.length - 1], '（最小/中位/最大）· 定位规则', n.locate_rules, '条 · 兜底', n.locate_fallback)
  const actHist = {}
  for (const e of n.event_activates) actHist[e.activates] = (actHist[e.activates] ?? 0) + 1
  console.log('  每件事激活病数分布：', Object.entries(actHist).map(([k, v]) => `${k} 张 × ${v} 件`).join(' · '))
  console.log('  一局候选数分布：', Object.entries(n.candidates).map(([k, v]) => `${k} 张 × ${v} 局`).join(' · '), '· 调子/候选冲突的局', n.voice_mismatch_runs)
  console.log('  素材台账：', `用到 ${n.material.used} 段 / 未用到 ${n.material.unused} 段（共 ${n.material.total}）`)
  console.log('  交出去的经历与疾病：profileOf() 的 experiences = 那件事的素材，diseases = 认下的那张')

  // ⑧ 阶段 7 的**界面接线**：那件事进叙事流 · 候选钉在底部 · 认下即落笔 · 言语随病
  //    （§十 的接线契约落到屏幕上没有。走一局真的点一遍，读渲染出来的 html。）
  const selectorQ = db.questions.find((q) => q.answers === 'complaint')
  {
    const state = clinic.state
    const blank = db.record.columns.find((c) => c.id === 'diagnosis').blank
    state.answers = {}
    state.signed = false
    state.disease = null
    clinic.render()
    click(root, { answerValue: 'sleep' })
    let guard = 0
    while (guard < 200) {
      const id = plan(db, state.answers).find((x) => state.answers[x] === undefined)
      if (!id) break
      const opts = optionsOf(db, map0.get(id))
      click(root, { answerValue: id === selectorQ.id ? opts.find((o) => o.id === 'sleep').id : opts[0].id })
      if (db.answers[map0.get(id).answers]?.multi && state.answers[id] === undefined) click(root, { answerCommit: '1' })
      guard += 1
    }
    const before = shell.innerHTML
    const ids = [...before.matchAll(/data-disease="([a-z_0-9]+)"/g)].map((m) => m[1])
    const limit = db.event_wiring.candidate.candidate_max
    const event = eventOf(db, openingJson, state)
    const checks = [
      ['那件事进叙事流', /data-turn-q="event"/.test(before)],
      [`认下诊断的回应（${ids.length} 张候选 · 上界 ${limit} · 数字键${/data-choice-index="1"/.test(before) ? '在' : '不在'}）`, ids.length > 0 && ids.length <= limit],
      ['认病之前诊断栏是空白态（不是空着不写）', before.includes(blank)],
      ['候选都在那件事的 activates 里', ids.length > 0 && ids.every((id) => (event?.activates ?? []).includes(id))],
    ]
    console.log('  认病之前：诊断栏空白态', before.includes(blank) ? '在' : '不在', '· 候选', ids.length, '张 · 上界', limit)
    if (ids.length) {
      const label = ddb.items.find((d) => d.id === ids[0]).label
      click(root, { disease: ids[0] })
      const after = shell.innerHTML
      const column = (() => {
        const at = after.indexOf('data-column="diagnosis"')
        const next = after.indexOf('data-column="', at + 1)
        return at < 0 ? '' : after.slice(at, next < 0 ? after.length : next)
      })()
      const voice = db.voices.items.find((v) => v.disease === ids[0] || (v.covers ?? []).includes(ids[0]))
      const voiceLine = voice ? db.event_wiring.ui.voice_of_disease.replace('{voice}', voice.screen_name) : null
      const profile = clinic.getProfile()
      checks.push(['诊断栏由医师落笔（院方笔迹 + 那一栏不再是空白态）', column.includes(label) && column.includes('oc-ink-hospital') && !column.includes(blank)])
      checks.push(['认下之后叙事流里补一条落笔', after.includes(db.event_wiring.ui.confirmed_note.replace('{label}', label))])
      checks.push([`言语随病（${voice ? voice.screen_name : '没有指纹代言'}）`, Boolean(voiceLine) && after.includes(voiceLine)])
      checks.push(['交出去的 profile 非空（experiences = 素材 · diseases = 认下的那张）', profile.experiences.length > 0 && profile.diseases.length === 1])
      console.log('  认下之后：诊断栏', column.includes(label) ? `医师写上了「${label}」` : '没写上', '· 言语随病', voiceLine && after.includes(voiceLine) ? '跟着走' : '没跟着走')
      console.log('  交出去的 profile：experiences', profile.experiences.length, '段素材 · diseases', profile.diseases.join(' / ') || '（无）')
    }
    const failed = checks.filter(([, ok]) => !ok)
    console.log('  阶段 7 界面接线：', failed.length ? `✗ ${failed.map(([name]) => name).join(' · ')}` : `${checks.length} 项全过`)
    if (failed.length) process.exitCode = 1
  }

  // ⑨ owner 2026-09-27 在真浏览器里看过成品之后的三条**形态裁定** + 一条追加（呈现层，与数据无关）：
  //    ① 纸不随每次点击滚到底 · ② 右栏只有一个滚动区 · ③ 调子色只画在选项上 · ④ 叙事流让回应整块进视野
  {
    const cssText = readFileSync(new URL('opening-clinic.css', moduleDir), 'utf8')
    // 结构判据要在**去掉注释**的 CSS 上跑：注释里也会出现 `.oc-now` 这类字眼，
    // 不剥掉的话 `[^{]*` 会一路吃到下一个规则的 `{`，把别人的规则体当成它的。
    const cssBare = cssText.replace(/\/\*[\s\S]*?\*\//g, '')
    const pageHtml = readFileSync(new URL('../../design/presentation/叙事界面原型.html', import.meta.url), 'utf8')
    const state = clinic.state
    state.answers = {}
    state.signed = false
    state.disease = null

    // ① 纸：同一栏里连着渲两次，位置留住（不是纸尾）；换栏那一次才把它滚进视野。
    const colAt = () => activeColumnId(db, state)
    paperScroll.scrollTop = 120
    clinic.render()
    clinic.render()
    const kept = paperScroll.scrollTop
    const startCol = colAt()
    const pending = currentQuestion(db, state)
    if (pending) state.answers[pending.id] = optionsOf(db, pending)[0].id
    const movedColumn = colAt() !== startCol
    paperScroll.scrollTop = 0
    clinic.render()
    const afterChange = paperScroll.scrollTop
    // `block:'nearest'` 的等价算法：把那一栏的下沿对齐视野下沿（桩里的数：300+200-400 = 100）。
    const nearest = paperColumn.offsetTop + paperColumn.offsetHeight - paperScroll.clientHeight

    const checks = [
      [`纸不随每次点击滚（同一栏渲两次后 scrollTop 仍是 ${kept}，不是纸尾 ${paperScroll.scrollHeight}）`, kept === 120 && kept !== paperScroll.scrollHeight],
      [`换栏那一次才把它滚进视野（${movedColumn ? `换栏 → scrollTop ${afterChange}，期望 ${nearest}` : '这一拍没换栏'}）`, afterChange === (movedColumn ? nearest : 0)],
    ]

    // ② 右栏只有一个滚动容器：回应块在叙事流之内，且 `.oc-responses` / `.oc-now` 都没有自己的 overflow。
    const blockOf = (selector) => [...cssBare.matchAll(new RegExp(`${selector}[^{]*\\{([^}]*)\\}`, 'g'))].map((m) => m[1])
    const scrolls = (body) => /overflow(-[xy])?\s*:\s*(auto|scroll)|max-height/.test(body)
    const htmlNow = shell.innerHTML
    const storyAt = htmlNow.indexOf('class="oc-story"')
    const nowAt = htmlNow.indexOf('data-responses="1"')
    const scrollers = [...new Set([...cssBare.matchAll(/\.(oc-[a-z-]+)[^{]*\{([^}]*)\}/g)]
      .filter(([, , body]) => /overflow(-y)?\s*:\s*(auto|scroll)/.test(body))
      .map(([, name]) => `.${name}`))]
    checks.push(['回应块在叙事流之内（data-responses 落在 .oc-story 里）', storyAt >= 0 && nowAt > storyAt])
    // 精确到那个容器类：`.oc-responses-label` 只是流里的一个标签，没有自己的滚动区，允许留着。
    checks.push(['`.oc-responses` 不再是独立滚动区（旧容器类名已撤）', !/class="oc-responses"/.test(htmlNow) && blockOf('\\.oc-responses(?![\\w-])').every((b) => !scrolls(b))])
    checks.push(['`.oc-now` 没有自己的 overflow / max-height', blockOf('\\.oc-now').every((b) => !scrolls(b))])
    checks.push(['右栏的滚动容器只有 .oc-story 一个', scrollers.includes('.oc-story') && !scrollers.some((s) => s.startsWith('.oc-responses') || s === '.oc-now')])

    // ③ 调子色：只画在选项上（细边 + 调子名），颜色写在 CSS 变量里，且**不铺整块底色**。
    const tones = ['depressive', 'manic', 'paranoid', 'compulsive']
    const toneClassed = [...htmlNow.matchAll(/class="oc-choice[^"]*oc-voice-(depressive|manic|paranoid|compulsive)/g)].map((m) => m[1])
    const voiceNames = [...htmlNow.matchAll(/class="oc-choice-voice">([^<]*)</g)].map((m) => m[1].trim())
    const toneBodies = blockOf('\\.oc-voice-(?:depressive|manic|paranoid|compulsive)')
    checks.push([`四个调子色类都在 CSS 里（${tones.filter((id) => new RegExp(`\\.oc-voice-${id}\\b`).test(cssText)).length}/4）且都走 CSS 变量（${tones.filter((id) => new RegExp(`var\\(--voice-${id}\\b`).test(cssText)).length}/4）`, tones.every((id) => new RegExp(`\\.oc-voice-${id}\\b`).test(cssText)) && tones.every((id) => new RegExp(`var\\(--voice-${id}\\b`).test(cssText))])
    checks.push([`变量与夜色 / 浅底那批同一处定义（页面 :root 里 ${tones.filter((id) => new RegExp(`--voice-${id}\\s*:`).test(pageHtml)).length}/4）`, tones.every((id) => new RegExp(`--voice-${id}\\s*:`).test(pageHtml))])
    checks.push(['调子色不铺整块底色（调子色的规则里没有 background）', toneBodies.length > 0 && toneBodies.every((b) => !/background/.test(b))])
    checks.push([`选项带调子色类名（本屏 ${toneClassed.length} 个）且调子名仍写着（${voiceNames.length} 个）——颜色是冗余信息`, toneClassed.length > 0 && voiceNames.length === toneClassed.length && voiceNames.every((x) => x.length > 0)])

    // ④ 追加裁定：叙事流的滚动 = **让回应整块进视野**（不是永远滚到最底）。两条分支各测一次。
    const GAP = 24
    const storyScenario = ({ storyHeight, view, top, height }) => {
      storyScroll.scrollHeight = storyHeight
      storyScroll.clientHeight = view
      nowBlock.offsetTop = top
      nowBlock.offsetHeight = height
      clinic.render()
      return storyScroll.scrollTop
    }
    const fits = storyScenario({ storyHeight: 1400, view: 400, top: 900, height: 200 })     // ① 装得下
    const tall = storyScenario({ storyHeight: 1600, view: 400, top: 700, height: 600 })     // ② 装不下
    const tight = storyScenario({ storyHeight: 400, view: 400, top: 100, height: 200 })     // ① 的下限 0
    const expectFits = Math.min(1400 - 400, 900 + 200 + GAP - 400)                          // 724
    const expectTall = Math.min(1600 - 400, 700 - GAP)                                      // 676
    storyScroll.scrollHeight = 1200                                                     // 拿不到尺寸 → 回落到滚到最底
    storyScroll.clientHeight = undefined
    nowBlock.offsetTop = 900
    nowBlock.offsetHeight = 200
    clinic.render()
    const fallbackTop = storyScroll.scrollTop
    storyScroll.clientHeight = 400
    checks.push([`叙事流：块 + ${GAP}px 装得下时滚到刚好带进视野（${fits}，期望 ${expectFits}）`, fits === expectFits])
    checks.push([`叙事流：块比视野还高时从块顶往上留 ${GAP}px 起读（${tall}，期望 ${expectTall}）`, tall === expectTall])
    checks.push(['叙事流：下限 0 / 上限最大滚动量（块顶在视野内时不倒着滚）', tight === 0])
    checks.push([`叙事流：拿不到 clientHeight 时回落到滚到最底（${fallbackTop} = scrollHeight）`, fallbackTop === storyScroll.scrollHeight])
    clinic.render()   // 复原到正常场景，后面的判据不受影响

    console.log('  纸的滚动：同栏两次渲染后 scrollTop', kept, '（纸尾是', paperScroll.scrollHeight, '）· 换栏', movedColumn ? `滚到 ${afterChange}` : '没发生')
    console.log('  叙事流滚动：装得下 →', fits, `（期望 ${expectFits}）· 装不下 →`, tall, `（期望 ${expectTall}）· 贴边 →`, tight, '· 拿不到尺寸 →', fallbackTop)
    console.log('  右栏滚动容器：', scrollers.join(' ') || '（一个都没有）')
    console.log('  调子色：本屏', toneClassed.length, '个选项带色 ·', voiceNames.length, '个写着调子名 ·', new Set(toneClassed).size, '套调子')
    const failed = checks.filter(([, ok]) => !ok)
    console.log('  形态裁定 ①②③④：', failed.length ? `✗ ${failed.map(([name]) => name).join(' · ')}` : `${checks.length} 项全过`)
    if (failed.length) process.exitCode = 1
  }

  process.exit(report.errors.length ? 1 : process.exitCode ?? 0)
}

const { root, shell } = mountDocument()
const { createOpeningClinic } = await import('../src/opening-clinic/index.js')
const clinic = createOpeningClinic({ trigger: null, required: true })
clinic.open()

const map = questionById(db)

/** 走一条路：每一步取第 k 档取值（越界取最后一档）。 */
function walk(branchId, k, { quiet = false } = {}) {
  const selector = db.questions.find((q) => q.answers === 'complaint')
  let state = clinic.state
  state.answers = {}
  state.signed = false
  clinic.render()
  click(root, { answerValue: branchId })
  let guard = 0
  while (guard < 200) {
    const ids = plan(db, state.answers)
    const id = ids.find((x) => state.answers[x] === undefined)
    if (!id) break
    const question = map.get(id)
    const opts = optionsOf(db, question)
    const picked = id === selector.id ? opts.find((o) => o.id === branchId) : opts[Math.min(k, opts.length - 1)]
    if (!quiet) console.log(`\n── 第 ${ids.filter((x) => state.answers[x] !== undefined).length + 1} 问 · ${question.ask}${question.followup ? '（追问）' : ''} → 答「${picked.label}」 ──`)
    click(root, { answerValue: picked.id })
    if (db.answers[question.answers]?.multi && state.answers[id] !== undefined && state.answers[id].length === 0) {
      click(root, { answerValue: picked.id })
    }
    if (!quiet) console.log(strip(shell.innerHTML).join('\n'))
    guard += 1
  }
  return plan(db, state.answers).length
}

if (!has('--all')) {
  console.log(strip(shell.innerHTML).join('\n'))
  process.exit(0)
}

const only = flag('--branch')
const branches = branchSummary(db).filter((b) => (only ? b.id === only : true))
const rows = []
for (const branch of branches) {
  const total = walk(branch.id, 0, { quiet: true })
  rows.push({ branch: branch.label, questions: total })
  console.log(`\n══════ 主诉「${branch.label}」：一局 ${total} 问 ══════`)
  walk(branch.id, 0)
  console.log('\n── 落款前的那张纸 ──')
  console.log(strip(shell.innerHTML).slice(-24).join('\n'))
}

console.log('\n══════ 一局问数汇总 ══════')
for (const row of rows) console.log(`  ${row.branch}：${row.questions} 问`)
console.log('签名：', /data-sign/.test(shell.innerHTML) ? '可签' : '（当前不在落款那一拍）')
