/**
 * 无头渲染：用最小 DOM 桩把开局界面渲染出来，打印结构（没有浏览器时的核对手段）。
 *
 *   bun web/scripts/render-cc.mjs            # 第一问（患者自述）
 *   bun web/scripts/render-cc.mjs --all      # 走完八问 + 池子 + 落款，逐段打印
 *   bun web/scripts/render-cc.mjs --check    # 只做形态自检（旧排版残留 / 自由文本输入）
 *
 * 它验证的是「一张纸 + 一问一答」这个形态本身：栏序列得出、答案写得进纸里、
 * 池子的条目逐条可点；它不验证视觉。
 */
import db from '../../data/opening.json' with { type: 'json' }
import ddb from '../../data/diseases.json' with { type: 'json' }

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

const click = (root, dataset) => {
  const attrs = Object.keys(dataset).map(
    (key) => `[data-${key.replace(/[A-Z]/g, (c) => `-${c.toLowerCase()}`)}]`,
  )
  const target = { closest: (selector) => (attrs.includes(selector) ? { dataset } : null) }
  for (const fn of root.listeners.click ?? []) fn({ target })
}

const { root, shell } = mountDocument()
const { createCharacterCreation } = await import('../src/character-creation/index.js')
const cc = createCharacterCreation({ trigger: null, required: true })
cc.open()

const strip = (html) => html
  .replace(/<div class="cc-record-head">[\s\S]*?<\/div>\s*<\/div>\s*<\/div>/, '<一般情况：页眉（只读 + 两笔可填）>')
  .replace(/<[^>]+>/g, '\n')
  .split('\n')
  .map((x) => x.trim())
  .filter(Boolean)

const sections = (html) => {
  const cols = [...html.matchAll(/data-column="([a-z]+)"/g)].map((m) => m[1])
  return cols
}

const args = new Set(process.argv.slice(2))

if (args.has('--check')) {
  const cls = [...shell.innerHTML.matchAll(/class="([^"]+)"/g)].flatMap((m) => m[1].split(/\s+/))
  // 旧排版：五屏步条（cc-header 里那个 ol）· 卡片网格 · 右侧统计栏 · 认识页的取值按钮
  const old = ['cc-experience-grid', 'cc-live-summary', 'cc-experience-card', 'cc-category-list',
    'cc-anchor-option', 'cc-anchor-form', 'cc-disease-grid', 'cc-attribute-grid', 'cc-mirror-screen', 'cc-centered']
  const leftovers = old.filter((c) => cls.includes(c))
  const forbidden = ['textarea', 'contenteditable', '<input', '锚点']
  console.log('旧排版类名残留：', leftovers.length ? leftovers.join(' · ') : '（无）')
  console.log('自由文本 / 内部词：', forbidden.filter((f) => shell.innerHTML.includes(f)).join(' · ') || '（无）')
  console.log('五屏步条（cc-header 里的 ol）：', /<header class="cc-header">[\s\S]*?<ol/.test(shell.innerHTML) ? '还在' : '（无）')
  console.log('栏目序列：', sections(shell.innerHTML).join(' → '))
  console.log('问诊条：', /cc-interview-bar/.test(shell.innerHTML) ? '在' : '不在')
  process.exit(0)
}

if (!args.has('--all')) {
  console.log(strip(shell.innerHTML).join('\n'))
  process.exit(0)
}

// 每一问的第一个可点取值（闭集来自数据：vocab 或主诉的自述表，脚本不自己列词）。
const firstValueOf = (q) => {
  const spec = q.answer_from === 'complaint' ? db.complaint.self_report : db.vocab[q.facet]
  if (q.facet === 'relation') return ['authority']
  return spec.multi ? [spec.values[0].id] : spec.values[0].id
}
for (const [i, q] of db.interview.questions.entries()) {
  const value = firstValueOf(q)
  if (Array.isArray(value)) {
    for (const v of value) click(root, { answerFacet: q.facet, answerValue: v })
  } else {
    click(root, { answerFacet: q.facet, answerValue: value })
  }
  console.log(`\n── 第 ${i + 1} 问 · ${q.ask} → 答 ${JSON.stringify(value)} ──`)
  console.log(strip(shell.innerHTML).join('\n'))
}

console.log('\n── 池子（既往史） ──')
const poolIds = [...shell.innerHTML.matchAll(/data-entry="(exp_\d{4})"/g)].map((m) => m[1])
console.log('池子条数：', poolIds.length, '·', poolIds.join(','))
for (const id of poolIds.slice(0, db.quota.total)) click(root, { entry: id })
console.log(strip(shell.innerHTML).slice(-16).join('\n'))

click(root, { 'pool-done': '' })
const cands = [...shell.innerHTML.matchAll(/data-disease="(dis_\d{4})"/g)].map((m) => m[1])
console.log('\n── 患者意见 ── 候选：', cands.join(','))
if (cands.length) click(root, { disease: cands[0] })
click(root, { stage: 'sign' })
console.log('\n── 落款 ──')
console.log(strip(shell.innerHTML).slice(-14).join('\n'))
click(root, { confirm: '' })
console.log('\n完成：', cc.completed, '· profile：', JSON.stringify(cc.getProfile()))
