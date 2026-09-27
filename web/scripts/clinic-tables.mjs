/**
 * 把 `design/presentation/开局门诊问诊.md` 里那几张表**跑出来**（生成物，勿手改）。
 *
 *   bun web/scripts/clinic-tables.mjs          # 全部四张表
 *   bun web/scripts/clinic-tables.mjs --runs   # 一局问数
 *   bun web/scripts/clinic-tables.mjs --columns# 栏目与落笔表
 *   bun web/scripts/clinic-tables.mjs --coverage# 参照 113 问的去向
 *   bun web/scripts/clinic-tables.mjs --bank   # 题库总表（长）
 *   bun web/scripts/clinic-tables.mjs --voices # 语言指纹表 + 拼句表
 *   bun web/scripts/clinic-tables.mjs --events # 阶段 7：那件事表 + 定位规则表 + 指纹挂病表 + 候选分布
 *
 * 文档里那几段是从这里复制过去的；改了数据就重跑这个脚本，别去手改文档里的表。
 */
import db from '../../data/opening_clinic.json' with { type: 'json' }
import odb from '../../data/opening.json' with { type: 'json' }
import ddb from '../../data/diseases.json' with { type: 'json' }
import {
  answerSetOf,
  branchSummary,
  eventDiseaseCandidates,
  eventRuleOf,
  isMulti,
  locateRules,
  optionsOf,
  plan,
  questionById,
  requiredQuestions,
  runCounts,
  validateClinic,
  voiceProfiles,
} from '../src/opening-clinic/opening-clinic.js'

const roster = ddb.items.filter((i) => i.always_on !== true)
const diseaseLabel = (id) => ddb.items.find((d) => d.id === id)?.label ?? id

const args = process.argv.slice(2)
const has = (n) => args.includes(n)
const all = args.length === 0

const out = []
const say = (line = '') => out.push(line)

if (all || has('--runs')) {
  const rows = runCounts(db)
  say('### 一局问数（生成物，勿手改）')
  say()
  say('| 主诉分支 | 分支自己的问数 | 一局最少 | 一局中位 | 一局最多 | 采样最长 | 追问全开的过估值 |')
  say('|---|--:|--:|--:|--:|--:|--:|')
  for (const r of rows) {
    say(`| ${r.label} | ${r.branch_questions} | ${r.min} | ${r.median} | ${r.max} | ${r.sampled_max} | ${r.upper_bound_all_followups} |`)
  }
  say()
  const report = validateClinic(db, { diseases: ddb })
  say(`题库 ${report.numbers.questions} 条 · 必问骨架 ${report.numbers.required} 问 · 主诉分支 ${report.numbers.branches} 个 · 敏感问题 ${report.numbers.sensitive} 问 ·`)
  say(`ask_mode 分布：${Object.entries(report.numbers.modes).map(([k, v]) => `${k} ${v}`).join(' · ')} · 主诉可拼路径 ${report.numbers.complaint_paths} 条 · 拒答枚举 ${report.numbers.refusal_cases} 局`)
  say()
}

if (all || has('--columns')) {
  say('### 栏目与落笔表（生成物，勿手改）')
  say()
  say('| 组 | 栏目（逐字） | 谁落笔 | 谁落的笔（fill） | 取值从哪来 | 空白态 | 出处 |')
  say('|---|---|---|---|---|---|---|')
  const groups = { homepage: '首页 · 一般情况', body: '病历记录（第十三条的顺序）' }
  for (const c of db.record.columns) {
    const src = c.value_from_source ?? (c.value_from_question ? `问诊 ${c.value_from_question}` : null)
      ?? (c.derive_from ? `现算：${c.derive_from.join(' + ')}` : null)
      ?? (c.value_from ? `${c.value_from}` : null)
      ?? (c.value ? `院方固定值：${c.value}` : '无')
    say(`| ${groups[c.group] ?? c.group} | ${c.label} | ${c.who === 'patient' ? '患者陈述' : '院方记录'} | ${c.fill} | ${src} | ${c.blank} | ${String(c.basis).slice(0, 120)} |`)
  }
  say()
  say('**本作不开放的法定首页项**（`record.not_open`，不上纸）：' + db.record.not_open.map((n) => `${n.label}（${n.why}）`).join('　'))
  say()
}

if (all || has('--coverage')) {
  say('### 参照 113 问的去向（生成物，勿手改）')
  say()
  say('| 参照 | 本作 id | 去向 | 说明 |')
  say('|--:|---|---|---|')
  const byRef = new Map()
  for (const q of db.questions) {
    const key = Number.isInteger(q.ref) ? q.ref : Math.floor(q.ref)
    if (!byRef.has(key)) byRef.set(key, [])
    byRef.get(key).push(q)
  }
  for (let i = 1; i <= db.meta.owner_reference_total; i += 1) {
    for (const q of byRef.get(i) ?? []) {
      const note = q.note ? String(q.note).slice(0, 70) : (q.required ? '必问' : (q.trigger ? `追问（${q.trigger.label}）` : '按分支问'))
      say(`| ${q.ref} | ${q.id} | ${q.ask_mode} | ${String(note).replaceAll('|', '/')} |`)
    }
  }
  say()
}

if (all || has('--bank')) {
  const label = db.module_labels
  say('### 题库总表（生成物，勿手改）')
  say()
  say('| id | 参照 | 模块 | 医生问法 | 去向 | 必问 | 触发 | 落栏 | 敏感 | 依据 |')
  say('|---|---|--:|---|---|:--:|---|---|---|---|')
  for (const q of [...db.questions].sort((a, b) => a.ref - b.ref)) {
    const spec = answerSetOf(db, q)
    const trigger = q.trigger ? `q=${q.trigger.q} ∈ ${(q.trigger.in ?? []).join('/')}${q.trigger.not_in ? ` ∉ ${q.trigger.not_in.join('/')}` : ''}` : ''
    const ask = q.ask_mode === 'player'
      ? `${q.ask}（${isMulti(db, q) ? `多选 ${spec.min_items}–${spec.max_items}` : '单选'}，共 ${spec.values.length + 1} 档）`
      : q.ask
    say(`| ${q.id} | ${q.ref} | ${label[q.module] ?? q.module} | ${ask.replaceAll('|', '/')} | ${q.ask_mode} | ${q.required ? '✓' : ''} | ${trigger} | ${q.column ?? ''} | ${q.sensitive ?? ''} | ${String(q.basis).slice(0, 90).replaceAll('|', '/')} |`)
  }
  say()
}

if (all || has('--voices')) {
  const playerQuestions = db.questions.filter((q) => q.ask_mode === 'player' && q.answers)
  const countOf = (voiceId) => playerQuestions.reduce((n, q) => n + answerSetOf(db, q).values.filter((v) => v.voice === voiceId).length, 0)
  const asksOf = (voiceId) => playerQuestions.filter((q) => answerSetOf(db, q).values.some((v) => v.voice === voiceId)).map((q) => q.id)
  say('### 语言指纹表（生成物，勿手改）')
  say()
  say('| id | 上屏名 | 一句话 | 打标档数 | 覆盖问数 | 落在哪些问 |')
  say('|---|---|---|---:|---:|---|')
  for (const v of db.voices.items) say(`| \`${v.id}\` | ${v.screen_name} | ${v.screen_note} | ${countOf(v.id)} | ${asksOf(v.id).length} | ${asksOf(v.id).join(' · ')} |`)
  say()
  say(`阈值 \`min_tagged\` = ${db.voices.min_tagged}（打标档不足这个数，这一局不算显出调子）；打了标的档共 ${playerQuestions.reduce((n, q) => n + answerSetOf(db, q).values.filter((v) => v.voice).length, 0)} 档。`)
  say()
  say('### 拼句表（生成物，勿手改）')
  say()
  say('| 栏目 | 句数 | 引用了几问 | 每一句用到的问 |')
  say('|---|--:|--:|---|')
  for (const [columnId, spec] of Object.entries(db.compose ?? {})) {
    const parts = spec.sentences.flatMap((s) => s.parts.map((p) => p.q))
    say(`| ${columnId} | ${spec.sentences.length} | ${new Set(parts).size} | ${spec.sentences.map((s) => `${s.id}(${s.parts.map((p) => p.q).join('+')})`).join(' · ')} |`)
  }
  say()
  const clauseCount = playerQuestions.reduce((n, q) => n + answerSetOf(db, q).values.filter((v) => v.clause).length, 0)
  say(`临床片段（\`clause\`）合计 ${clauseCount} 条。`)
  say()
}

if (has('--events')) {
  const rule = eventRuleOf(odb)
  say('### 那件事（生成物，勿手改）')
  say()
  say(`一局恰一件（\`event_rule.one_event_per_run === true\`）；每件事的扩展位下限 ${rule.expansions_min} 档（必须覆盖 ${rule.expansion_axes_required.join(' · ')} 四位）；每件事激活 ${rule.activates_min}–${rule.activates_max} 张病；属性效果 = 素材合计（\`effects_terms_max\` = ${rule.effects_terms_max} 项）。`)
  say()
  say('| id | 那件事 | 一句话（claim） | 扩展位 | 覆盖的位 | 激活的病 | 素材 | 属性效果 |')
  say('|---|---|---|--:|---|---|---:|---|')
  for (const e of odb.events) {
    const axes = [...new Set(e.expansions.map((x) => x.facet))].join(' · ')
    const acts = e.activates.map((id) => `${diseaseLabel(id)}\`${id}\``).join(' · ')
    const eff = Object.entries(e.effects.attributes).map(([k, v]) => `${odb.attributes.labels[k]}${v > 0 ? '+' : ''}${v}`).join(' ')
    say(`| \`${e.id}\` | ${e.title} | ${e.claim} | ${e.expansions.length} | ${axes} | ${acts} | ${e.source_experiences.length} | ${eff} |`)
  }
  say()
  const used = new Set(odb.events.flatMap((e) => e.source_experiences))
  say(`素材台账：288 段里被用到 **${used.size}** 段，未被任何事件用到 **${odb.experiences.length - used.size}** 段（只报数，不报错——owner 待裁 7 的默认 (a)）。`)
  say()
  say('### 定位规则（生成物，勿手改）')
  say()
  say('按顺序判，第一条 when 全部成立的胜出；都不成立取兜底件。用到的问：' + locateRules(db).map((r) => r.q).filter((q, i, a) => a.indexOf(q) === i).join(' · '))
  say()
  say(`| # | 规则 | 问 | 取值 | → 那件事 | 依据（节录） |`)
  say('|---|---|---|---|---|---|')
  for (const [i, r] of locateRules(db).entries()) {
    const evt = odb.events.find((e) => e.id === r.event)
    const values = r.in.map((v) => optionsOf(db, questionById(db).get(r.q)).find((o) => o.id === v)?.label ?? v).join(' / ')
    say(`| ${i + 1} | \`${r.id}\` | \`${r.q}\` | ${values} | \`${r.event}\` ${evt?.title ?? ''} | ${String(r.basis).slice(0, 60)}… |`)
  }
  say(`| — | 兜底 | — | — | \`${db.event_wiring.locate.fallback_event}\` ${odb.events.find((e) => e.id === db.event_wiring.locate.fallback_event)?.title ?? ''} | 诱因不明确那一类（教材自己承认它存在） |`)
  say()
  say('### 语言指纹挂病（生成物，勿手改）')
  say()
  say('| 指纹 | 上屏名 | 主病 | 还代言 | 代言合计 |')
  say('|---|---|---|---|--:|')
  for (const v of voiceProfiles(db)) {
    const all = [v.disease, ...(v.covers ?? [])].filter(Boolean)
    say(`| \`${v.id}\` | ${v.screen_name} | \`${v.disease}\` ${diseaseLabel(v.disease)} | ${(v.covers ?? []).map((id) => `${diseaseLabel(id)}\`${id}\``).join(' · ')} | ${all.length} |`)
  }
  say()
  const voiced = new Set(voiceProfiles(db).flatMap((v) => [v.disease, ...(v.covers ?? [])]).filter(Boolean))
  say(`名册 ${roster.length} 张病，被指纹代言 ${[...voiced].filter((id) => roster.some((r) => r.id === id)).length} 张；没有任何指纹代言的：${roster.filter((r) => !voiced.has(r.id)).map((r) => r.id).join(' / ') || '（无）'}。`)
  say()
  say('### 一局的候选数分布（生成物，勿手改）')
  say()
  const selector = db.questions.find((q) => q.answers === 'complaint')
  const hist = {}
  for (const branch of branchSummary(db)) {
    const branchQ = plan(db, { [selector.id]: branch.id })
    const maxOpts = Math.max(1, ...branchQ.map((id) => optionsOf(db, questionById(db).get(id)).length))
    const combos = []
    for (let k = 0; k < maxOpts; k += 1) {
      const answers = {}
      for (const id of branchQ) {
        const opts = optionsOf(db, questionById(db).get(id))
        if (opts.length) answers[id] = opts[Math.min(k, opts.length - 1)].id
      }
      combos.push(answers)
    }
    const refused = {}
    for (const id of branchQ) refused[id] = db.refuse.id
    combos.push(refused)
    for (const answers of combos) {
      const n = eventDiseaseCandidates(db, odb, ddb, { answers, signed: false, disease: null }).candidates.length
      hist[n] = (hist[n] ?? 0) + 1
    }
  }
  say('| 候选数 | 出现次数 | 什么时候 |')
  say('|--:|--:|---|')
  for (const n of Object.keys(hist).sort()) {
    say(`| ${n} | ${hist[n]} | ${n === '1' ? '这一局说话的调子已经显出来（打标档 ≥ `min_tagged`）——收窄到那一套指纹代言的那张' : '调子还没显出来——4 张全摆出来由玩家挑'} |`)
  }
  say()
}

if (all) {
  const required = requiredQuestions(db)
  say('### 必问骨架与分支（生成物，勿手改）')
  say()
  say(`必问骨架 ${required.length} 问：${required.map((q) => q.id).join(' · ')}`)
  say()
  for (const b of branchSummary(db)) say(`- **${b.label}**（${b.id}）：${b.questions.join(' · ')}`)
  say()
  say('一个主诉分支被选中的那几问，连同主诉选择器自己：')
  say()
  say('| 主诉取值 | 分支问数 |')
  say('|---|--:|')
  for (const b of branchSummary(db)) say(`| ${b.label} | ${b.questions.length} |`)
}

console.log(out.join('\n'))
