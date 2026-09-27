/**
 * 开局门诊病历 · **契约层**（无状态纯函数）。
 *
 * 数据权威：`data/opening_clinic.json`（题库 · 答案闭集 · 分支规则 · 病历栏目与每一笔 · 全部上屏文案
 * · 阶段 7 的 `event_wiring` 接线口径）。**事件侧的两份权威在别的文件里，本文件只读**：
 * `data/opening.json` 的 `events` / `event_rule`（那件事 · 扩展位 · 激活的病 · 素材）与
 * `data/diseases.json` 的 `items` / `candidate_rule`（病卡与候选口径）。
 *
 * 本文件**不含任何界面文案**（状态提示语除外，且它们也来自数据）；它只做六件事：
 *
 *   1. 出题      `plan` / `currentQuestion` / `progressOf`
 *   2. 分支推进  `applyAnswer` / `reAnswer`（分支的唯一权威是数据里每一问的 `trigger`）
 *   3. 落笔      `composeColumn` / `paperColumns` / `chiefComplaint`（许多档答案**整理成整段句子**，
 *                不是一问一行；依据见 `design/presentation/开局门诊问诊.md` §十一）
 *   4. 言语      `voiceTally` / `observationRows`（怎么说话就是病在哪儿现形：嘴上说的 `label` 带语言
 *                指纹，纸上写的 `clause` 不动）
 *   5. 那件事    `eventOf` / `eventExpansions` / `eventDiseaseCandidates` / `confirmDisease` /
 *                `diagnosisEntry` / `voiceOfDisease` / `settleEventAttributes`（阶段 7：一局恰一件
 *                诱因事件 → 它激活的病 → 玩家认下一张 → 医师写上诊断栏）
 *   6. 校验      `validateClinic`（开发期函数；**没有任何 CI 在跑它**）
 *
 * 边界（AGENTS.md §二 拦截规则）：只服务开局 / Web 演示，不得引入 C# 引擎或神经模拟系统的任何概念；
 * 战斗相关内容一律不碰。7 扇 `paused` 的遭遇门原样保留、不渲染。
 *
 * 形态不变式（提示词 §一）：玩家只有三种笔——**答 · 认 · 签**；没有自由文本输入。
 * 本文件里出现的一切取值都来自数据；`refuse` 那一档是全局登记的，逐问沿用。
 */

import ddb from '../../../data/diseases.json'
import odbDefault from '../../../data/opening.json'

// ── 基本取用 ──────────────────────────────────────────────────────────────

export const initialState = () => ({ answers: {}, signed: false })

/** 参照编号是唯一的排序键：owner 参照的 113 问本来就是按问诊先后编的。 */
const byRef = (a, b) => a.ref - b.ref

// 同一份 db 只排一次、只建一次索引（校验器要跑几千次 plan，靠这个把它压到亚秒级）。
const sortedCache = new WeakMap()
const indexCache = new WeakMap()
export function sortedQuestions(db) {
  if (!sortedCache.has(db)) sortedCache.set(db, [...db.questions].sort(byRef))
  return sortedCache.get(db)
}
export function questionById(db) {
  if (!indexCache.has(db)) indexCache.set(db, new Map(sortedQuestions(db).map((q) => [q.id, q])))
  return indexCache.get(db)
}
export const answerSetOf = (db, question) => (question?.answers ? db.answers[question.answers] ?? null : null)
export const probesOf = (db, question) => {
  const known = new Map(db.probes.list.map((p) => [p.id, p]))
  return (question?.probes ?? []).map((id) => known.get(id)).filter(Boolean)
}

export const refuseIds = (db) => new Set([db.refuse.id, ...(db.refuse.aliases ?? [])])
export const isRefuse = (db, value) => refuseIds(db).has(value)
export const refusalRecord = (db) => db.refuse.record

/**
 * 某一问在界面上能点的全部取值：闭集 + 全局的那一档「不愿说」。
 *
 * ⚠️ 闭集里**自己就带拒答档**时不再追加第二个（q001 的主诉选择器就有 `decline`，它是
 * `refuse.aliases` 里的一员）——否则同一屏上会并排出现两个「不愿说」按钮，
 * 一个走闭集内的档、一个走全局档，看起来像两个不同的意思。
 */
export function optionsOf(db, question) {
  const spec = answerSetOf(db, question)
  if (!spec) return []
  if (spec.values.some((v) => isRefuse(db, v.id))) return [...spec.values]
  return [...spec.values, { id: db.refuse.id, label: db.refuse.label, record: db.refuse.record }]
}
export const isMulti = (db, question) => Boolean(answerSetOf(db, question)?.multi)
export const answerLimitOf = (db, question) => {
  const spec = answerSetOf(db, question)
  return { min: spec?.min_items ?? 1, max: spec?.max_items ?? 1 }
}

/** 这一问在病历上落笔要用的那一档取值（`record` 缺省回落为 `label`）。 */
export function optionOf(db, question, valueId) {
  const spec = answerSetOf(db, question)
  if (isRefuse(db, valueId)) return { id: db.refuse.id, label: db.refuse.label, record: db.refuse.record }
  return spec?.values.find((v) => v.id === valueId) ?? null
}

/** 取值上屏的那一行字（患者口吻，直接来自数据）。 */
export function answerTextOf(db, question, value) {
  const ids = Array.isArray(value) ? value : [value]
  return ids.map((id) => optionOf(db, question, id)?.record ?? null).filter(Boolean).join('、')
}

const isAnsweredValue = (db, question, value) => {
  if (Array.isArray(value)) {
    const { min, max } = answerLimitOf(db, question)
    if (value.length < min || value.length > max) return false
    if (value.some((v) => isRefuse(db, v))) return value.length === 1
    return value.every((v) => Boolean(optionOf(db, question, v)) && !isRefuse(db, v))
  }
  return Boolean(optionOf(db, question, value))
}

// ── 分支：`trigger` 是唯一权威 ─────────────────────────────────────────────

function triggerOk(db, trigger, answers) {
  if (!trigger) return true
  const value = answers[trigger.q]
  if (value === undefined) return false
  const values = Array.isArray(value) ? value : [value]
  if (trigger.in && !values.some((v) => trigger.in.includes(v))) return false
  if (trigger.not_in && values.some((v) => trigger.not_in.includes(v))) return false
  return true
}

/**
 * 本局要问哪些题、按什么顺序问。
 *
 * 顺序 = **参照编号**（那份参照本身就是按门诊问诊的先后编的：开场主诉 → 症状群 → 风险 →
 * 物质与躯体 → 既往家族 → 个人史 → 检查 → 结束），分支 = 每一问自己的 `trigger`。
 * 医方观察类（`observed`）与并入 / 撤回 / 保留的那几问**不进问诊条**。
 */
export function plan(db, answers = {}) {
  const out = []
  for (const q of sortedQuestions(db)) {
    if (q.ask_mode === 'player' && triggerOk(db, q.trigger, answers)) out.push(q.id)
  }
  return out
}

export function answersInPlan(db, answers = {}) {
  const ids = new Set(plan(db, answers))
  return Object.fromEntries(Object.entries(answers).filter(([id]) => ids.has(id)))
}

/** 这一局当前要问的那一问（答完了返回 null）。 */
export function currentQuestion(db, state) {
  const map = questionById(db)
  const id = plan(db, state.answers).find((qid) => state.answers[qid] === undefined)
  return id ? map.get(id) ?? null : null
}

export function progressOf(db, state) {
  const ids = plan(db, state.answers)
  const answered = ids.filter((id) => state.answers[id] !== undefined).length
  return { index: Math.min(answered + 1, ids.length), answered, total: ids.length }
}

/** 答一句。回退的是**因为这一答而不再成立的那些答案**（分支自己的因果）。 */
export function applyAnswer(db, state, questionId, value) {
  const question = questionById(db).get(questionId)
  if (!question || question.ask_mode !== 'player') {
    return { state, dropped: [], rejected: 'not_a_player_question' }
  }
  if (!isAnsweredValue(db, question, value)) {
    return { state, dropped: [], rejected: 'value_not_in_closed_set' }
  }
  const draft = { ...state.answers, [questionId]: value }
  const kept = answersInPlan(db, draft)
  const dropped = Object.keys(draft).filter((id) => !(id in kept))
  return { state: { ...state, answers: kept }, dropped, rejected: null }
}

/** 「改一改」：回到那一问重答，从它往后写下的字一起退回去。 */
export function reAnswer(db, state, questionId) {
  const ids = plan(db, state.answers)
  const at = ids.indexOf(questionId)
  if (at < 0) return { state, dropped: [], rejected: 'not_in_plan' }
  const keep = new Set(ids.slice(0, at))
  const kept = Object.fromEntries(Object.entries(state.answers).filter(([id]) => keep.has(id)))
  const dropped = Object.keys(state.answers).filter((id) => !(id in kept))
  return { state: { ...state, answers: kept, signed: false }, dropped, rejected: null }
}

export const isComplete = (db, state) => currentQuestion(db, state) === null

// ── 落笔：答案写成纸上的字 ─────────────────────────────────────────────────

// ── 拼句：把许多档答案整理成连贯的病史（不再是「一问一行」） ────────────────
//
// 依据：《精神病学》第 7 版 第三章第三节（二）4（入院检索 §5.7）——
// 「记录病史应如实描述，但应进行**整理加工使其条理清楚、简明扼要**……对一些重要的症状可
// 记录患者原话。记录时要避免用医学术语。」所以纸上写的是**整理过的句子**，不是把患者嘴里的
// 词一行一行照抄；模板与每一档的临床片段都在数据里（`compose` / `values[].clause`）。

/** 这一档落进句子里的那一段（`clause` 缺省回落为 `record`，再缺省回落为 `label`）。 */
export function clauseOf(db, question, valueId) {
  if (isRefuse(db, valueId)) return null
  const option = optionOf(db, question, valueId)
  return option?.clause ?? option?.record ?? option?.label ?? null
}

/** 多选时把几档的临床片段用「，」并列——所以数据里的 clause 必须能这么并列。 */
export function clauseTextOf(db, question, value) {
  const ids = Array.isArray(value) ? value : [value]
  const parts = ids.map((id) => clauseOf(db, question, id)).filter(Boolean)
  return parts.join('，')
}

const isRefused = (db, value) => (Array.isArray(value) ? value.some((v) => isRefuse(db, v)) : isRefuse(db, value))

/**
 * 把一个栏目拼成整段病史。
 *
 * 句子的形状、顺序与依据都在数据的 `compose.<栏目>` 里；**没答的与答成「不愿说」的那一段整段跳过**
 * （连它的 `pre` / `post` 一起跳过）；一个句子里所有段都跳过时整句不写。
 * 返回里同时给出每一句用到了哪几问（`parts`）与这一栏里**未答**的问（`unanswered`）。
 */
export function composeColumn(db, state, columnId) {
  const spec = db.compose?.[columnId]
  if (!spec) return null
  const questionOf = questionById(db)
  const sentences = []
  const unanswered = []

  for (const sentence of spec.sentences ?? []) {
    const parts = []
    for (const part of sentence.parts ?? []) {
      const question = questionOf.get(part.q)
      const value = state.answers[part.q]
      if (!question || value === undefined) continue
      if (isRefused(db, value)) {
        unanswered.push({ questionId: part.q, lead: question.lead || question.module || part.q })
        continue
      }
      const text = clauseTextOf(db, question, value)
      if (!text) continue
      parts.push({ questionId: part.q, text, pre: part.pre ?? '', post: part.post ?? '' })
    }
    if (!parts.length) continue
    const opener = sentence.open ?? ''
    const body = parts
      .map((part, index) => {
        // 第一段只在**句首没有引导语**时才把开头的标点吃掉（不然会剩下一个孤零零的逗号）；
        // 「患者于…」里的「于」这类非标点的前缀一律留下。
        const pre = index === 0 && !opener ? part.pre.replace(/^[，、；：,;]+/, '') : part.pre
        return `${pre}${part.text}${part.post}`
      })
      .join('')
    sentences.push({
      id: sentence.id,
      basis: sentence.basis ?? null,
      text: `${opener}${body}${sentence.close ?? '。'}`,
      parts: parts.map(({ questionId, text }) => ({ questionId, text })),
    })
  }

  for (const question of writersOf(db, columnId)) {
    if (question.value_from_question) continue
    const value = state.answers[question.id]
    if (value === undefined || !isRefused(db, value)) continue
    if (unanswered.some((u) => u.questionId === question.id)) continue
    unanswered.push({ questionId: question.id, lead: question.lead || question.module || question.id })
  }

  return { text: sentences.map((s) => s.text).join(''), sentences, unanswered }
}

/** 这一栏是不是「整段病史」（有 compose 模板的才是；主诉与首页那几笔不是）。 */
export const isProseColumn = (db, columnId) => Boolean(db.compose?.[columnId])

/**
 * 这一答现在写在纸上的**那一句**是什么（整句，不是它贡献的那一段）。
 *
 * 两个来源：① 整段病史的栏目 → 它落在的那一句现在读起来的样子；
 * ② 现算栏（主诉）→ 那一栏此刻成品的样子（「睡不着 三四个月」）。
 * 都用不上（首页那几笔）时返回 null，由调用方回落到这一档自己的字。
 */
export function writtenLineOf(db, state, question) {
  if (!question?.column) return null
  const column = db.record.columns.find((c) => c.id === question.column)
  if (!column) return null
  if (isProseColumn(db, question.column)) {
    const sentence = composeColumn(db, state, question.column)?.sentences.find((s) => s.parts.some((p) => p.questionId === question.id))
    if (sentence) return sentence.text
  }
  if (column.fill === 'derived') return chiefComplaint(db, state)
  return null
}

/** 主诉栏：法定格式是「主要症状（或体征）+ 持续时间」，两半都必须拼得出来。 */
export function chiefComplaint(db, state) {
  const map = questionById(db)
  const part = (qid) => {
    const q = map.get(qid)
    const value = state.answers[qid]
    if (value === undefined) return null
    if (Array.isArray(value) && value.some((v) => isRefuse(db, v))) return refusalRecord(db)
    if (isRefuse(db, value)) return refusalRecord(db)
    return answerTextOf(db, q, value)
  }
  const symptom = part('q003')
  const duration = part('q005')
  if (symptom === null && duration === null) return null
  return `${symptom ?? refusalRecord(db)} ${duration ?? refusalRecord(db)}`
}

/** 这一栏由哪几问落笔（按问诊顺序）。 */
export const writersOf = (db, columnId) =>
  sortedQuestions(db).filter((q) => q.ask_mode === 'player' && q.column === columnId)

/**
 * 纸上的这一栏现在由哪几问答出来的（按问诊顺序）。
 *
 * ⚠️ 这里的 `text` 是**这一答落进句子的那一段**（`clause`），不是患者嘴里的原话——纸上不照抄对话词。
 * 它只用于「改一改」与回溯：整栏的字由 `composeColumn()` 拼（见 `paperColumns`）。
 */
export function rowsOf(db, state, columnId) {
  return writersOf(db, columnId)
    .filter((q) => state.answers[q.id] !== undefined)
    .map((q) => ({
      questionId: q.id,
      ask: q.ask,
      lead: q.lead ?? '',
      text: clauseTextOf(db, q, state.answers[q.id]) || answerTextOf(db, q, state.answers[q.id]),
      ink: db.record.ink.patient.id,
    }))
}

const looksUnwritten = (value) => value === null || value === undefined || value === ''

/**
 * 整张纸：每一栏此刻写着什么、谁落的笔、没落笔时显示什么。
 *
 * `ctx.character` 来自人物来源（正典 / 自建），`ctx.signed` 来自落款那一拍。
 *
 * 病史那四栏（现病史 / 既往史 / 个人史 / 家族史）是**整段拼出来的句子**（`composeColumn`，模板在
 * `compose` 里），不是「一问一行」——这是阶段 6 改掉的那件事。`rows` 仍逐条指得回是哪一问答的，
 * 但那只用于「改一改」与回溯，不再当纸上的行。
 *
 * 精神检查那几行（`record.observations`）**由院方写、玩家只读**；其中带 `derive` 的行按这一趟
 * 问出来的东西现算（说话的调子 / 某一问的答案），取不到时回落到那一行自己的写法。
 */
export function paperColumns(db, state, ctx = {}) {
  const character = ctx.character ?? null
  const signed = ctx.signed ?? state.signed
  const legacy = ctx.legacyCharacterSource ?? {}
  const identity = legacy.identity ?? {}
  const questionOf = questionById(db)

  return db.record.columns.map((column) => {
    const base = {
      id: column.id,
      group: column.group,
      label: column.label,
      who: column.who,
      fill: column.fill,
      blank: column.blank,
      basis: column.basis,
      note: column.note ?? null,
      screen_note: column.screen_note ?? null,
      value_from: column.value_from ?? null,
      rows: [],
    }

    if (column.fill === 'blank') return { ...base, text: column.blank, resolved: false, ink: db.record.ink.hospital.id }

    if (column.fill === 'patient_sign') {
      return { ...base, text: signed ? (ctx.signedText ?? db.ui.signed) : column.blank, resolved: signed }
    }

    if (column.value_from === 'observations') {
      return {
        ...base,
        text: '',
        resolved: false,
        ink: db.record.ink.hospital.id,
        rows: observationRows(db, state).map((o) => ({
          questionId: null,
          lead: `${o.label}：`,
          text: o.text,
          ink: db.record.ink.hospital.id,
          basis: o.basis,
          derivedFrom: o.derivedFrom,
        })),
      }
    }

    if (column.value_from_question) {
      const q = questionOf.get(column.value_from_question)
      const value = state.answers[column.value_from_question]
      if (value === undefined) return { ...base, text: column.blank, resolved: false }
      return { ...base, text: answerTextOf(db, q, value), resolved: true, rows: rowsOf(db, state, column.id) }
    }

    if (column.value_from_source) {
      const key = column.value_from_source
      if (key === 'character.name') {
        const text = character?.name ?? null
        return { ...base, text: text ?? column.blank, resolved: Boolean(text), ink: db.record.ink.patient.id }
      }
      if (key === 'character.gender') {
        const text = character?.genderLabel ?? null
        return { ...base, text: text ?? column.blank, resolved: Boolean(text), ink: db.record.ink.patient.id }
      }
      if (key === 'character.hospital_name') {
        const text = identity.hospital_name ?? column.blank
        return { ...base, text, resolved: true, ink: db.record.ink.hospital.id }
      }
      return { ...base, text: column.blank, resolved: false }
    }

    // 阶段 7：诊断栏那一笔由本局「认」下的病落笔，**医师的笔**（who = hospital，fill = derived）。
    // 它必须排在 fill === 'derived' 那一支**之前**——现算栏（主诉）也走 derived，两者靠 value_from 分。
    if (column.value_from === 'confirmed_disease') {
      const entry = diagnosisEntry(db, openingDbOf(ctx), ctx.diseases ?? ddb, state)
      return {
        ...base,
        text: entry.resolved ? entry.text : column.blank,
        resolved: entry.resolved,
        ink: db.record.ink.hospital.id,
        disease: entry.disease,
        diseaseLabel: entry.label,
        disease_basis: entry.basis,
        conflict: entry.conflict,
        rows: entry.resolved
          ? [{ questionId: null, lead: `${column.label}：`, text: entry.text, ink: db.record.ink.hospital.id, disease_basis: entry.basis }]
          : [],
      }
    }

    if (column.fill === 'derived') {
      const text = chiefComplaint(db, state)
      if (looksUnwritten(text)) return { ...base, text: column.blank, resolved: false }
      const unavailable = (column.derive_from ?? []).some((qid) => state.answers[qid] === undefined)
      return {
        ...base,
        text,
        resolved: true,
        ink: unavailable ? db.record.ink.patient.id : db.record.ink.hospital.id,
        rows: (column.derive_from ?? [])
          .filter((qid) => state.answers[qid] !== undefined)
          .map((qid) => {
            const q = questionOf.get(qid)
            return { questionId: qid, ask: q.ask, lead: q.lead ?? '', text: answerTextOf(db, q, state.answers[qid]), ink: db.record.ink.patient.id }
          }),
      }
    }

    if (column.fill === 'patient_input') {
      const rows = rowsOf(db, state, column.id)
      const composed = composeColumn(db, state, column.id)
      if (composed) {
        return {
          ...base,
          composed: true,
          text: composed.text,
          sentences: composed.sentences,
          unanswered: composed.unanswered,
          resolved: rows.length > 0,
          ink: db.record.ink.patient.id,
          rows,
        }
      }
      return {
        ...base,
        composed: false,
        text: rows.map((r) => `${r.lead}${r.text}`).join('\n'),
        resolved: rows.length > 0,
        ink: db.record.ink.patient.id,
        rows,
      }
    }

    // hospital：院方已经写好，玩家只读
    return { ...base, text: column.value ?? column.blank, resolved: true, ink: db.record.ink.hospital.id }
  })
}

/** 现在填到哪一栏（正在填的那一栏高亮）。 */
export function activeColumnId(db, state) {
  if (state.signed) return null
  const question = currentQuestion(db, state)
  if (question) return question.column
  return 'historian_sign'
}

export const canSign = (db, state) => isComplete(db, state) && !state.signed
export const sign = (state) => ({ ...state, signed: true })

// ── 阶段 7：那件事 → 病 → 诊断栏 ──────────────────────────────────────────
//
// owner 裁定（提示词 §二）：经历的第一职责是**激活它那张病**；一局的经历是**一件事**，不是十段散点；
// 那件事要**经得起扩展**。所以本段的链条是：
//
//   问诊答案 → eventOf（恰一件）→ eventExpansions（扩展位）→ eventDiseaseCandidates（≤4）
//     → confirmDisease（玩家「认」）→ diagnosisEntry（医师落笔）→ voiceOfDisease / settleEventAttributes
//
// 每一段的规则都写在数据里，代码只执行：
//   定位规则  data/opening_clinic.json 的 `event_wiring.locate`（有序规则表 + 无条件兜底）
//   事件本身  data/opening.json 的 `events`（含 `expansions` / `activates` / `effects` / `source_experiences`）
//   候选上界  data/opening.json 的 `event_rule.candidate_max`（与 data/diseases.json 的 `candidate_rule` 同值）

/** 事件侧的权威数据（`data/opening.json`）。调用方可以传自己那一份（测试用），默认是仓库里那一份。 */
export const openingDbOf = (ctx = {}) => ctx.openingDb ?? odbDefault

export const eventsOf = (odb) => odb.events ?? []
export const eventById = (odb, id) => eventsOf(odb).find((e) => e.id === id) ?? null
export const eventRuleOf = (odb) => odb.event_rule ?? {}

export const locateWiring = (db) => db.event_wiring?.locate ?? null
export const locateRules = (db) => locateWiring(db)?.rules ?? []
export const locateFallbackEventId = (db) => locateWiring(db)?.fallback_event ?? null
export const expandWiring = (db) => db.event_wiring?.expand ?? null
export const candidateWiring = (db) => db.event_wiring?.candidate ?? null
export const voiceWiring = (db) => db.event_wiring?.voice ?? null
export const diagnosisWiring = (db) => db.event_wiring?.diagnosis ?? null

/** 一条定位规则在这份答案下成不成立（`in` 里有一个就成立；没答 = 不成立）。 */
export function locateRuleMatches(rule, answers = {}) {
  const value = answers[rule.q]
  if (value === undefined) return false
  const values = Array.isArray(value) ? value : [value]
  return values.some((v) => (rule.in ?? []).includes(v))
}

/**
 * 一局的那件事（**恰好一件**）。
 *
 * 顺序判 `event_wiring.locate.rules`，第一条成立的胜出；一条都不成立取 `fallback_event`。
 * 规则表的末条是无条件兜底（写进数据），所以「恰一件」是**结构保证**：任何答案组合下都返回一条，
 * 不会返回 null、也不会返回两条。返回里带上**是哪一条规则定的**（`ruleId`）或 `fallback: true`，
 * 供审计与界面复述「因为你说……」。
 */
export function seedEvent(db, odb, answers = {}) {
  for (const rule of locateRules(db)) {
    if (locateRuleMatches(rule, answers)) {
      return { id: rule.event, ruleId: rule.id, fallback: false, rule, event: eventById(odb, rule.event) }
    }
  }
  const id = locateFallbackEventId(db)
  return { id, ruleId: null, fallback: true, rule: null, event: eventById(odb, id) }
}

/** 同上，只取那件事本身（`state` 或一份裸答案都能传）。 */
export function eventOf(db, odb, state = {}) {
  const answers = state?.answers ?? state ?? {}
  return seedEvent(db, odb, answers).event
}

// ── 扩展位 ────────────────────────────────────────────────────────────────

/** 那件事的扩展位（每一档写明：落在哪个 facet、由哪一问的哪一档答出来、嘴上说什么、纸上写什么）。 */
export const eventExpansions = (odb, event) => event?.expansions ?? []

/** 这一档扩展位被玩家答出来了没有（多选问看「答的里面有没有这一档」，单选问看等不等）。 */
export function expansionAnswered(db, expansion, answers = {}) {
  const value = answers[expansion.q]
  if (value === undefined) return false
  const values = Array.isArray(value) ? value : [value]
  return values.includes(expansion.value_id)
}

/** 已答的扩展位（在事件自己的顺序上），以及没答的那些。 */
export function eventExpansionState(db, odb, event, answers = {}) {
  const all = eventExpansions(odb, event)
  const answered = all.filter((x) => expansionAnswered(db, x, answers))
  const pending = all.filter((x) => !expansionAnswered(db, x, answers))
  return { all, answered, pending }
}

/**
 * 扩展位那一档落在纸上的字（`clause`）与落在哪一栏。
 *
 * ⚠️ 它**不是**第二套拼句引擎：`clause` 就是这一问这一档在本文件 `compose` 模板里已经用到的那一段，
 * 纸由现有的 `composeColumn` 拼（见 `paperColumns`）。本函数只是把「这一档属于这件事」这件事
 * 连同它的文案一起交出来，供界面复述与校验器比对。
 */
export const expansionClause = (expansion) => expansion?.clause ?? null
export const expansionColumn = (expansion) => expansion?.column ?? null
export const expansionFacet = (expansion) => (expansion ? { facet: expansion.facet, value: expansion.value } : null)

/** 扩展位在数据里的稳定身份（`q.value_id`），界面与 `exclude` 规则都用它。 */
export const expansionIdOf = (expansion) => expansion?.id ?? null

// ── 候选：那件事激活的病 ──────────────────────────────────────────────────

/**
 * 本局的患者意见栏能点到哪几张病。
 *
 * 规则（数据在 `data/opening.json` 的 `event_rule.candidate_and_voice` 与
 * `data/diseases.json` 的 `candidate_rule`）：
 *   ① 候选 = 那件事的 `activates` 减去**已答扩展位**声明排除的病（`expansion.exclude`）；
 *   ② 一局说话的调子定下来之后（`voiceTally` 显出了 dominant），再收窄到**该调子代言的那一张**；
 *   ③ 上界 = `event_rule.candidate_max`（4）。
 *
 * ⚠️ 那件事每件事的 `activates` 都**一套指纹一张**（4 张），所以第 ② 步至多收窄到 1 张——
 * 「怎么说话就是在说哪张病」（owner 第 7 条）。调子还没显出来时 4 张全摆出来由玩家挑。
 */
export function eventDiseaseCandidates(db, odb, ddb, state = {}) {
  const answers = state?.answers ?? state ?? {}
  const { event } = seedEvent(db, odb, answers)
  const limit = eventRuleOf(odb).candidate_max ?? candidateWiring(db)?.candidate_max ?? 4
  if (!event) return { event: null, events: [], excluded: [], candidates: [], narrowed: [], limit, overflow: false }

  const expanded = eventExpansions(odb, event).filter((x) => expansionAnswered(db, x, answers))
  const excluded = []
  for (const x of expanded) {
    for (const id of x.exclude ?? []) excluded.push({ id, by: expansionIdOf(x), why: x.basis ?? null })
  }
  const excludedIds = new Set(excluded.map((x) => x.id))
  const roster = new Map(ddb.items.map((d) => [d.id, d]))
  const activated = (event.activates ?? [])
    .filter((id) => !excludedIds.has(id))
    .map((id) => ({
      id,
      label: roster.get(id)?.label ?? id,
      plain: roster.get(id)?.plain ?? null,
      from: { kind: 'activates', event: event.id, title: event.title },
    }))

  // ② 按说话的调子收窄（调子由 voiceTally 现算；还没显出来就不收窄）
  const { dominant } = voiceTally(db, state)
  const narrowed = dominant ? activated.filter((c) => voiceOfDisease(db, c.id)?.id === dominant) : [...activated]
  // 收窄会把候选清空时**回落到不收窄**（数据坏了也不该让这一局走不下去；校验器会报 candidate_without_voice）
  const candidates = narrowed.length ? narrowed : activated
  return {
    event,
    events: event.activates ?? [],
    excluded,
    activated,
    narrowed: narrowed.map((c) => c.id),
    voice: dominant,
    candidates,
    limit,
    overflow: candidates.length > limit,
  }
}

/**
 * 「因为你有那件事：……」——候选为什么在这儿，写成一句话给界面复述。
 *
 * 出处：owner 第 2 条裁定「经历首先需要满足能够激活疾病」。文案模板与那件事的 `title` / `claim`
 * 都来自数据，本函数不新增中文界面文案字面量（除连接用的标点）。
 */
export function candidateBasis(db, odb, ddb, state, diseaseId) {
  const { event, candidates, excluded } = eventDiseaseCandidates(db, odb, ddb, state)
  if (!event) return null
  const hit = candidates.find((c) => c.id === diseaseId)
  if (!hit) return null
  const reason = db.event_wiring?.ui?.candidate_basis ?? null
  return {
    disease: hit.id,
    label: hit.label,
    event: event.id,
    title: event.title,
    claim: event.claim,
    summary: event.summary,
    screen: reason ? reason.replace('{title}', event.title).replace('{label}', hit.label) : null,
    excluded: excluded.filter((x) => x.id === diseaseId),
  }
}

// ── 认：玩家从候选里认下一张（可反悔）────────────────────────────────────

export const confirmedDiseaseId = (state) => state?.disease ?? null

/**
 * 认下一张病（传 null 或 undefined = 反悔，退回没认的状态）。
 *
 * 落点的选择见 owner 待裁 4 的默认 (a)：**对话里一枚回应**，不新开屏、不在纸上加「患者意见」栏
 * （门诊初诊的法定栏目里没有这一栏，自造栏目违反「不许自造」）。
 * 拒绝理由码：`not_in_candidates`（不在本局候选里）/ `voice_disease_conflict`（与这一局说话的调子收敛到的病不一致）。
 */
export function confirmDisease(db, odb, ddb, state, diseaseId) {
  if (diseaseId === null || diseaseId === undefined) return { state: { ...state, disease: null }, rejected: null }
  const { candidates } = eventDiseaseCandidates(db, odb, ddb, state)
  if (!candidates.some((c) => c.id === diseaseId)) return { state, rejected: 'not_in_candidates' }
  const conflict = diseaseVoiceConflict(db, state, diseaseId)
  if (conflict) return { state, rejected: 'voice_disease_conflict', conflict }
  return { state: { ...state, disease: diseaseId }, rejected: null }
}

// ── 言语：语言指纹挂在病上 ────────────────────────────────────────────────

/** 这张病由哪一套语言指纹代言（`disease` 是主病，`covers` 是它同时代言的其他病）。 */
export function voiceOfDisease(db, diseaseId) {
  if (!diseaseId) return null
  for (const profile of voiceProfiles(db)) {
    if (profile.disease === diseaseId) return profile
    if ((profile.covers ?? []).includes(diseaseId)) return profile
  }
  return null
}

/** 这一套指纹代言哪些病（主病在前）。 */
export function diseasesOfVoice(db, voiceId) {
  const profile = voiceById(db).get(voiceId)
  if (!profile) return []
  return [profile.disease, ...(profile.covers ?? [])].filter(Boolean)
}

/** 一份病 id 清单里，哪些没有任何指纹代言（空数组 = 全都有人代言）。 */
export const diseasesWithoutVoice = (db, diseaseIds) => [...new Set(diseaseIds)].filter((id) => !voiceOfDisease(db, id))

/**
 * 这一局说话的调子与这张病对不对得上。
 *
 * 🔧 阶段 6 的「调子不等于诊断」自阶段 7 起由 owner 第 6 条裁定取代：**调子必须与认下的病一致**。
 * 返回 null = 一致（或这一局还没显出调子、没认病）；否则给出两边各是谁。
 */
export function diseaseVoiceConflict(db, state, diseaseId) {
  const tally = voiceTally(db, state)
  if (!tally.dominant || !diseaseId) return null
  const voice = voiceOfDisease(db, diseaseId)
  if (!voice) return { voice: tally.dominant, voiceLabel: tally.dominantLabel, disease: diseaseId, expected: null, reason: 'disease_without_voice' }
  if (voice.id === tally.dominant) return null
  return { voice: tally.dominant, voiceLabel: tally.dominantLabel, disease: diseaseId, expected: { id: voice.id, label: voice.screen_name }, reason: 'voice_mismatch' }
}

// ── 落笔：诊断栏那一笔（医师的笔，不是玩家的）────────────────────────────

/**
 * 诊断栏此刻写着什么。
 *
 * 出处：《病历书写基本规范》第二章第十三条（初诊病历记录书写内容含「诊断及治疗意见和医师签名」）；
 * 门诊侧省级规范把这一栏叫「初步印象」（河南细则第二十三条）。`who` 是 `hospital`——玩家只做「认」，
 * 落笔的是接诊医师。**不写医嘱、不写量表分、不写护理等级**（owner 第 7 条裁定）。
 */
export function diagnosisEntry(db, odb, ddb, state = {}, ctx = {}) {
  const column = db.record.columns.find((c) => c.id === 'diagnosis') ?? null
  const blank = column?.blank ?? null
  const id = confirmedDiseaseId(state)
  if (!id) return { disease: null, label: null, text: blank, resolved: false, ink: db.record.ink.hospital.id, column, basis: null, conflict: null }
  const known = ddb.items.find((d) => d.id === id)
  const basis = candidateBasis(db, odb, ddb, state, id)
  return {
    disease: id,
    label: known?.label ?? id,
    text: known?.label ?? id,
    resolved: true,
    ink: db.record.ink.hospital.id,
    column,
    basis,
    conflict: diseaseVoiceConflict(db, state, id),
  }
}

// ── 结算：那件事 → 属性（替代「十段和 = +2」）────────────────────────────

/**
 * 那件事的属性结算。返回形状与 `character-creation/opening.js` 的 `settleAttributes` **逐字段一致**
 * （`raw` / `clamped` / `band` / `overflow` / `totalRaw`），这样下游换来源不用改读法。
 *
 * 一个数，不是两个：事件的 `effects.attributes` 按数据契约**等于**它 `source_experiences` 那几段素材
 * 属性效果的合计（判据 `event_effects_not_from_material`），而 `profileOf().experiences` 带出去的
 * 正是那几段素材 id ⇒ `opening-runtime.js` 用旧路径结算出来的数与这里一模一样。
 *
 * ⚠️ 与存量的差别：净值 = 素材数 × `effects_rule.net`（2），本批每件事 4 段 ⇒ 一局的原始总和是 8，
 * 而存量「十段和」是 20。对序章三条检定阈值（3 / 5 / 7）的影响见口径文档的待裁表。
 */
export function settleEventAttributes(odb, eventId, base = odb.base_attributes) {
  const event = eventById(odb, eventId)
  if (!event) throw new Error(`未知事件 id: ${eventId}`)
  const raw = {}
  for (const k of odb.attributes.ids) raw[k] = base[k]
  for (const [k, d] of Object.entries(event.effects.attributes)) raw[k] += d
  const { min, max } = odb.attribute_bounds
  const clamped = {}
  const band = {}
  const overflow = {}
  for (const k of odb.attributes.ids) {
    clamped[k] = Math.min(max, Math.max(min, raw[k]))
    overflow[k] = raw[k] - clamped[k]
    band[k] = bandOf(odb, clamped[k])
  }
  return {
    raw,
    clamped,
    band,
    overflow,
    totalRaw: odb.attributes.ids.reduce((s, k) => s + raw[k], 0),
    from: { event: eventId, materials: [...(event.source_experiences ?? [])] },
  }
}

/** 分数 → 档位（与 `opening.js` 的 `bandOf` 同判据，读的是同一张档位表）。 */
export function bandOf(odb, score) {
  const tier = odb.bands.tiers.find((b) => score >= b.min && score <= b.max)
  if (!tier) throw new Error(`分数 ${score} 无对应档位（档位表未覆盖 ${odb.attribute_bounds.min}–${odb.attribute_bounds.max}）`)
  return { id: tier.id, ordinal: tier.ordinal, label: tier.label }
}

/** 一局的属性结算：那件事（已答扩展位不另计属性——数据里没有第二份 effects 词表，见口径文档）。 */
export function settleRun(odb, state = {}) {
  const id = state.event ?? null
  if (!id) return null
  return settleEventAttributes(odb, id)
}

// ── 语言指纹：怎么说话，就是病在哪儿现形 ──────────────────────────────────
//
// 依据（数据侧口径见 `data/opening_clinic.json` 的 `voices` 块）：每一档取值可以在 `voice` 上打标，
// 打了标的档，**患者说出来的那句话就带这一套言语特征**（`label`），而纸上写的字（`clause`）不受影响——
// 「嘴上怎么说」与「文书上怎么写」是两件事。一局里打标的档计数，决定这一局**说话的调子**。

export const voiceProfiles = (db) => db.voices?.items ?? []
export const voiceById = (db) => new Map(voiceProfiles(db).map((v) => [v.id, v]))
export const voiceOf = (db, question, valueId) => optionOf(db, question, valueId)?.voice ?? null

/**
 * 这一局他说话的调子。
 *
 * 规则（可机核、不靠感觉）：只数打了标的档；`min_tagged`（数据里给，默认 3）以下不算数；
 * 并列时取**最后出现**的那一套（他最后落在哪一边）。返回 null 表示这一局没显出调子。
 */
export function voiceTally(db, state) {
  const counts = {}
  const lastSeen = {}
  const labels = {}
  for (const profile of voiceProfiles(db)) { counts[profile.id] = 0; lastSeen[profile.id] = -1; labels[profile.id] = profile.screen_name }
  let order = 0
  let tagged = 0
  for (const question of sortedQuestions(db)) {
    if (question.ask_mode !== 'player') continue
    const value = state.answers[question.id]
    if (value === undefined) continue
    for (const id of Array.isArray(value) ? value : [value]) {
      const voice = voiceOf(db, question, id)
      if (!voice || !(voice in counts)) continue
      counts[voice] += 1
      lastSeen[voice] = order
      tagged += 1
    }
    order += 1
  }
  const min = db.voices?.min_tagged ?? 3
  let dominant = null
  if (tagged >= min) {
    for (const profile of voiceProfiles(db)) {
      const id = profile.id
      if (counts[id] === 0) continue
      if (dominant === null
        || counts[id] > counts[dominant]
        || (counts[id] === counts[dominant] && lastSeen[id] > lastSeen[dominant])) dominant = id
    }
  }
  return {
    counts,
    labels,
    tagged,
    dominant,
    dominantLabel: dominant ? labels[dominant] : null,
    profile: dominant ? voiceById(db).get(dominant) ?? null : null,
  }
}

// ── 精神检查：六行观察里能由这一趟问出来的，就现算 ────────────────────────
//
// 数据里每一行可以给 `derive`：从**言语指纹**（`voice`，阶段 7 起因指纹挂在病上而优先按**病**取）
// 或从**某一问的答案**（`answer`）落笔；取不到时回落到这一行自己的 `text`（空白态也是它）。
// 行仍然由院方写、玩家只读。

export function observationRows(db, state, ctx = {}) {
  const tally = voiceTally(db, state)
  const questionOf = questionById(db)
  // 阶段 7：认了病就按**病**取（owner 第 6 条：疾病同时驱动言语与精神检查）；
  // 还没认病时回落到按**调子**取——阶段 6 的行为一字不变，旧的观察行测试因此全绿。
  const confirmed = confirmedDiseaseId(state)
  const spoken = confirmed ? voiceOfDisease(db, confirmed) : null
  const profile = spoken ?? tally.profile
  return (db.record.observations ?? []).map((row) => {
    const base = { label: row.label, basis: row.basis ?? null, derivedFrom: null }
    const derive = row.derive
    if (derive?.from === 'voice' && profile) {
      const text = derive.table?.[profile.id]
      if (text) {
        return {
          ...base,
          text,
          derivedFrom: spoken
            ? { kind: 'disease', id: confirmed, label: spoken.screen_name, voice: profile.id }
            : { kind: 'voice', id: tally.profile.id, label: tally.profile.screen_name },
        }
      }
    }
    if (derive?.from === 'answer' && derive.q) {
      const question = questionOf.get(derive.q)
      const value = state.answers[derive.q]
      const id = Array.isArray(value) ? value.find((v) => !isRefuse(db, v)) : value
      const text = id && id !== db.refuse.id ? derive.table?.[id] : null
      if (question && text) return { ...base, text, derivedFrom: { kind: 'answer', id: derive.q, label: question.lead || question.ask } }
    }
    return { ...base, text: row.text ?? '', derivedFrom: null }
  })
}

// ── 对话：把已答的问还原成一段医患对话 ────────────────────────────────────

/**
 * 一答在**对话里**怎么念（患者说的是什么）。
 *
 * ⚠️ 与 `answerTextOf` 分工不同，两处都要有：
 *   - 对话里念 `label`（玩家点的那一句原话，例如「不愿说」）；
 *   - 病历上写 `record`（文书里的写法，例如「未答」）。
 * 把两者混成一个，就会出现「患者嘴上说未答」或者「病历里写不愿说」。
 */
export function answerLineOf(db, question, value) {
  const ids = Array.isArray(value) ? value : [value]
  return ids.map((id) => optionOf(db, question, id)?.label ?? null).filter(Boolean).join('、')
}

/**
 * **对话日志**：把这一局的问答还原成「医师问一句 → 患者答一句 → 医师落笔」的序列。
 *
 * 它**不是**第二份状态：从 `state.answers` + `plan()` 现算，所以「改一改」回到某一问时，
 * 那段之后的对话会一起退回去——不存在一份会漂的日志副本。
 * 只收 `ask_mode === 'player'` 的问（`observed` 是医师的观察、`withheld` 按安全底线不问，
 * 两者都不该出现在对话里）。
 *
 * 每一项：`{ kind, id, text, ... }`，`kind` ∈ `system`（敏感提示）· `doctor` · `patient` · `note`（落笔）。
 * 患者那一句用的是 `label`（**他嘴里的话**，打了语言指纹标的那一档就带那一套的语气），
 * 落笔那一句用的是 `clause`（**纸上写的字**）——两处刻意分开，纸上不照抄对话词。
 */
export function dialogueTurns(db, state) {
  const turns = []
  const noteTemplate = db.ui.write_note ?? '医师落笔：{text}'
  for (const q of sortedQuestions(db)) {
    if (q.ask_mode !== 'player') continue
    const value = state.answers[q.id]
    if (value === undefined) continue
    const level = q.sensitive ? db.sensitivity_levels?.[q.sensitive] : null
    if (level) {
      turns.push({ kind: 'system', id: `${q.id}:note`, label: level.label, text: level.content_note })
    }
    turns.push({
      kind: 'doctor',
      id: q.id,
      text: q.ask,
      module: q.module ?? null,
      moduleLabel: db.module_labels?.[q.module] ?? null,
      required: q.required === true,
      followup: Boolean(q.followup),
      triggerLabel: q.trigger?.label ?? null,
    })
    const ids = Array.isArray(value) ? value : [value]
    const voice = ids.map((id) => voiceOf(db, q, id)).find(Boolean) ?? null
    const profile = voice ? voiceById(db).get(voice) ?? null : null
    turns.push({
      kind: 'patient',
      id: q.id,
      text: answerLineOf(db, q, value),
      refuse: ids.some((v) => isRefuse(db, v)),
      written: answerTextOf(db, q, value),
      voice,
      voiceLabel: profile?.screen_name ?? null,
      voiceNote: profile?.screen_note ?? null,
    })
    const written = ids.some((v) => isRefuse(db, v)) ? db.refuse.record : clauseTextOf(db, q, value)
    if (written) {
      // 落笔那一句写的是**纸上此刻那一段的样子**：能拼句的栏目给整句（「患者因睡眠差来诊。」），
      // 其余（主诉与首页那几笔）给这一档自己的字。这就是「边谈边写」看得见的那一下。
      const sentence = writtenLineOf(db, state, q) ?? written
      turns.push({
        kind: 'note',
        id: q.id,
        lead: q.lead ?? '',
        text: noteTemplate.replace('{text}', sentence).replace('{lead}', q.lead ?? ''),
        ink: db.record.ink.patient.id,
      })
    }
  }
  return turns
}

/**
 * 交给下游（对话运行时 / 序章）的那份东西。
 *
 * 🔧 **阶段 7 的验收硬标准**（提示词 §六）：一局走完，`experiences` 与 `diseases` **非空且有据**——
 * 这一屏以前把两个数组写死成空，属性恒为 0、疾病分支恒空，而且**没有测试兜底**。
 *
 *   `experiences` = 那件事的 `source_experiences`（它扩写自的那几段存量素材，`exp_####`）。
 *                   ⚠️ 必须是 `data/opening.json` 里**真实存在**的记录 id：`opening-runtime.js:71`
 *                   会直接把它交给 `settleAttributes(db, [...])`，而那个函数对未知 id 是 **throw**。
 *   `diseases`    = 玩家**认下**的那一张（没认就是空数组——`opinion` 阶段允许一张都不认）。
 *
 * `clinic` 里带出那件事与候选，供序章 / 调试复述；`voice` 仍然是这一局说话的调子。
 */
export function profileOf(db, state, ctx = {}) {
  const character = ctx.character ?? {}
  const odb = openingDbOf(ctx)
  const ddbHere = ctx.diseases ?? ddb
  const tally = voiceTally(db, state)
  const { event, ruleId, fallback } = seedEvent(db, odb, state.answers ?? {})
  const candidates = eventDiseaseCandidates(db, odb, ddbHere, state)
  const confirmed = confirmedDiseaseId(state)
  return {
    id: 'opening_clinic',
    label: db.meta.title,
    experiences: [...(event?.source_experiences ?? [])],
    diseases: confirmed ? [confirmed] : [],
    source: character.source ?? null,
    ...(character.name ? { name: character.name } : {}),
    ...(character.gender ? { gender: character.gender } : {}),
    clinic: {
      stage: state.signed ? 'signed' : 'interview',
      answers: { ...state.answers },
      voice: tally.dominant ? { id: tally.dominant, label: tally.dominantLabel, counts: { ...tally.counts } } : null,
      event: event
        ? {
          id: event.id,
          title: event.title,
          claim: event.claim,
          rule: ruleId,
          fallback,
          expansions: eventExpansionState(db, odb, event, state.answers ?? {}).answered.map(expansionIdOf),
        }
        : null,
      candidates: candidates.candidates.map((c) => c.id),
      disease: confirmed,
    },
  }
}

// ── 报数：一局问多少 ──────────────────────────────────────────────────────

/** 主诉分支：从 q001 的答案反查（分支的唯一权威仍是每一问的 `trigger`）。 */
export function branchSummary(db) {
  const selector = db.questions.find((q) => q.trigger === null && q.required && q.answers === 'complaint')
    ?? db.questions.find((q) => q.answers === 'complaint')
  const spec = db.answers[selector.answers]
  const own = new Set([selector.id])
  return spec.values
    .filter((v) => !isRefuse(db, v.id))
    .map((v) => ({
      id: v.id,
      label: v.record ?? v.label,
      questions: plan(db, { [selector.id]: v.id }).filter((id) => !own.has(id) && questionById(db).get(id).trigger),
    }))
}

/** 所有分支同时触发全部追问时的一局问数上限（追问全开的过估）。 */
export function upperBoundFor(db, branchId) {
  const map = questionById(db)
  const selector = db.questions.find((q) => q.answers === 'complaint')
  const ids = new Set(plan(db, { [selector.id]: branchId }))
  let grew = true
  while (grew) {
    grew = false
    for (const q of sortedQuestions(db)) {
      if (q.ask_mode !== 'player' || ids.has(q.id)) continue
      if (q.trigger && ids.has(q.trigger.q)) { ids.add(q.id); grew = true }
    }
  }
  return ids.size
}

/**
 * 在某个主诉分支里找**一局最多能问多少**。
 *
 * 病态情形不靠猜：用固定种子的伪随机搜索在闭集上采样（同一颗种子必得同一结果），
 * 记下采样到的最长一局。它不是严格上界（严格上界是 `upperBoundFor`，那个数字把所有
 * 追问同时打开，实际不可能同时成立），但它是**真的走得到的局**。
 */
export function maxRunLength(db, branchId, samples = 800) {
  const selector = db.questions.find((q) => q.answers === 'complaint')
  const map = questionById(db)
  const pool = plan(db, { [selector.id]: branchId })
  let seed = 20260927
  const rnd = () => { seed = (seed * 1103515245 + 12345) % 2147483648; return seed / 2147483648 }
  let best = { length: 0, answers: null }
  for (let i = 0; i < samples; i += 1) {
    const answers = { [selector.id]: branchId }
    for (const id of pool) {
      const opts = optionsOf(db, map.get(id))
      if (!opts.length) continue
      answers[id] = opts[Math.floor(rnd() * opts.length)].id
    }
    const p = plan(db, answers)
    if (p.length > best.length) best = { length: p.length, answers }
  }
  return best
}

/** 枚举一局：把每一问都取第 k 档（越界取最后一档），外加「全部拒答」那一局。 */
function runCountFor(db, branchId, answers) {
  const selector = db.questions.find((q) => q.answers === 'complaint')
  const draft = { ...answers, [selector.id]: branchId }
  return plan(db, draft).length
}

export function runCounts(db) {
  const rows = []
  for (const branch of branchSummary(db)) {
    const sizes = []
    const selector = db.questions.find((q) => q.answers === 'complaint')
    const branchQ = plan(db, { [selector.id]: branch.id })
    const maxOpts = Math.max(1, ...branchQ.map((id) => optionsOf(db, questionById(db).get(id)).length))
    for (let k = 0; k < maxOpts; k += 1) {
      const answers = {}
      for (const id of branchQ) {
        const opts = optionsOf(db, questionById(db).get(id))
        if (!opts.length) continue
        answers[id] = opts[Math.min(k, opts.length - 1)].id
      }
      sizes.push(runCountFor(db, branch.id, answers))
    }
    const refused = {}
    for (const id of branchQ) refused[id] = db.refuse.id
    sizes.push(runCountFor(db, branch.id, refused))
    if (!sizes.length) sizes.push(runCountFor(db, branch.id, {}))
    const sorted = [...sizes].sort((a, b) => a - b)
    rows.push({
      id: branch.id,
      label: branch.label,
      branch_questions: branch.questions.length,
      min: sorted[0],
      max: sorted[sorted.length - 1],
      median: sorted.length % 2 ? sorted[(sorted.length - 1) / 2] : Math.round((sorted[sorted.length / 2 - 1] + sorted[sorted.length / 2]) / 2),
      sampled_max: maxRunLength(db, branch.id).length,
      upper_bound_all_followups: upperBoundFor(db, branch.id),
      sampled: sizes.length,
    })
  }
  return rows
}

export const requiredQuestions = (db) => sortedQuestions(db).filter((q) => q.ask_mode === 'player' && q.required)

// ── 校验（开发期；没有任何 CI 在跑它） ────────────────────────────────────

const collectStrings = (value, out = []) => {
  if (typeof value === 'string') out.push(value)
  else if (Array.isArray(value)) value.forEach((v) => collectStrings(v, out))
  else if (value && typeof value === 'object') Object.values(value).forEach((v) => collectStrings(v, out))
  return out
}

const collectKeys = (value, out = []) => {
  if (Array.isArray(value)) value.forEach((v) => collectKeys(v, out))
  else if (value && typeof value === 'object') {
    for (const [k, v] of Object.entries(value)) { out.push(k); collectKeys(v, out) }
  }
  return out
}

/** 把主诉那一行拼出来用的「最小答案集」：只答 q003 与 q005。 */
const complaintOnly = (db, symptomId, durationId) => ({ q003: symptomId, q005: durationId })

export function validateClinic(db, { diseases = ddb, opening = odbDefault } = {}) {
  const errors = []
  const warnings = []
  const err = (code, detail) => errors.push({ code, detail })
  const warn = (code, detail) => warnings.push({ code, detail })
  const odb = opening

  // 1. 参照 113 问一条都不丢
  const refs = new Set(db.questions.map((q) => q.ref))
  for (let i = 1; i <= db.meta.owner_reference_total; i += 1) {
    if (!refs.has(i) && !refs.has(i + 0.5)) err('reference_question_missing', `参照第 ${i} 问没有对应记录`)
  }

  const mode = {
    player: 0, observed: 0, merged: 0, withheld: 0, reserved: 0,
  }
  const sensitivity = new Set(Object.keys(db.sensitivity_levels))
  const probeIds = new Set(db.probes.list.map((p) => p.id))
  const columnIds = new Set(db.record.columns.map((c) => c.id))

  for (const q of db.questions) {
    if (!(q.ask_mode in mode)) err('ask_mode_unknown', `${q.id} 的 ask_mode「${q.ask_mode}」不在词表里`)
    else mode[q.ask_mode] += 1

    if (!q.basis) err('question_without_basis', `${q.id} 没有依据`)

    if (q.ask_mode === 'player') {
      const spec = answerSetOf(db, q)
      if (!spec) err('question_without_closed_set', `${q.id} 没有闭集`)
      else {
        if (spec.values.length < 2) err('closed_set_too_small', `${q.id} 的闭集只有 ${spec.values.length} 档`)
        const seen = new Set()
        for (const v of spec.values) {
          if (seen.has(v.id)) err('closed_set_duplicate_value', `${q.id} 的取值 ${v.id} 重复`)
          seen.add(v.id)
          if (v.id === db.refuse.id) err('closed_set_redefines_refuse', `${q.id} 自己又定义了一遍「不愿说」`)
        }
        for (const v of spec.values) {
          const text = `${v.label}${v.record ?? ''}`
          for (const name of diseases.items.map((d) => d.label)) {
            if (name && text.includes(name)) err('answer_names_diagnosis', `${q.id} 的取值「${v.label}」含病名「${name}」`)
          }
        }
      }
      // 每一问都有「不愿说」，并按敏感标记分级
      if (!db.refuse?.id || !db.refuse?.record) err('refuse_missing', '全局的「不愿说」没有登记')
      const level = q.sensitive ? db.refuse.policy.sensitive : db.refuse.policy.plain
      if (level !== 'required' && level !== 'optional') err('refuse_policy_unknown', `${q.id} 的拒答分级取不到`)
      if (!q.column || !columnIds.has(q.column)) err('question_column_unknown', `${q.id} 指向了不存在的栏目「${q.column}」`)
      if (!q.lead) warn('question_without_lead', `${q.id} 在纸上落笔时没有引导语（可能是故意的：主诉那两问）`)
    }

    if (q.sensitive) {
      if (!sensitivity.has(q.sensitive)) err('sensitivity_unknown', `${q.id} 的敏感标记「${q.sensitive}」不在词表里`)
      if (!db.sensitivity_levels[q.sensitive]?.content_note) err('sensitive_without_content_note', `${q.id} 没有内容提示语`)
    }

    if (q.ask_mode === 'observed' && !q.observed_note) err('observed_without_note', `${q.id} 是医方观察却没有写观察记录`)
    if (['merged', 'withheld', 'reserved'].includes(q.ask_mode) && !q.note) err('question_without_note', `${q.id} 是 ${q.ask_mode} 却没写理由`)

    for (const p of q.probes ?? []) if (!probeIds.has(p)) err('probe_unknown', `${q.id} 引用了不存在的追问层「${p}」`)

    if (q.trigger) {
      const target = db.questions.find((x) => x.id === q.trigger.q)
      if (!target) err('trigger_unknown_question', `${q.id} 的分支指向了不存在的 ${q.trigger.q}`)
      else {
        if (target.ref >= q.ref) err('trigger_forward_reference', `${q.id} 的分支指向了后面的 ${q.trigger.q}（顺序会失效）`)
        const spec = answerSetOf(db, target)
        for (const v of q.trigger.in ?? []) {
          if (!spec?.values.some((x) => x.id === v)) err('trigger_value_unknown', `${q.id} 的分支取值 ${v} 不在 ${target?.id} 的闭集里`)
        }
      }
      if (!q.trigger.label) err('trigger_without_label', `${q.id} 的分支没有上屏理由`)
    }
  }

  // 2. 栏目出处：每一栏都要指得到检索记录里的条目
  for (const c of db.record.columns) {
    if (!c.basis) err('column_without_basis', `栏目「${c.label}」没有出处`)
    if (!['hospital', 'patient'].includes(c.who)) err('column_who_unknown', `栏目「${c.label}」的 who 不在词表里`)
    if (!['hospital', 'patient_input', 'patient_sign', 'derived', 'blank'].includes(c.fill)) {
      err('column_fill_unknown', `栏目「${c.label}」的 fill「${c.fill}」不在词表里`)
    }
    if (c.who === 'patient' && c.fill === 'hospital') err('column_hospital_side_writable', `栏目「${c.label}」标明是患者笔迹却由院方写`)
    if (!c.blank) err('column_without_blank', `栏目「${c.label}」没写「没落笔时显示什么」`)
  }

  // 3. 上屏文案不漏内部词 / 不出现自由文本入口
  const internal = db.text_limits.internal_words
  const uiStrings = [
    ...collectStrings(db.ui),
    ...db.questions.flatMap((q) => [q.ask, q.lead, q.trigger?.label]),
    ...db.questions.flatMap((q) => (q.answers ? collectStrings(db.answers[q.answers]) : [])),
    ...collectStrings(db.record.observations),
    ...collectStrings(db.refuse),
    // 阶段 7：这一屏新说的话（接线口径里的上屏文案）与那件事自己的文案，同一套 lint
    ...collectStrings(db.event_wiring?.ui ?? {}),
    ...(odb.events ?? []).flatMap((e) => [e.title, e.summary, e.claim]),
    ...(odb.events ?? []).flatMap((e) => (e.expansions ?? []).map((x) => x.label)),
  ].filter(Boolean)
  for (const s of uiStrings) {
    for (const w of internal) {
      if (String(s).includes(w)) err('copy_leaks_internal', `上屏文案「${String(s).slice(0, 24)}」含内部词「${w}」`)
    }
  }
  for (const k of collectKeys({ ui: db.ui, answers: db.answers, questions: db.questions.map(({ id, ask, lead, trigger, answers, ...rest }) => rest) })) {
    for (const w of internal) if (k === w) err('copy_leaks_internal', `数据键名「${k}」是内部词`)
  }

  // 4. 主诉：每一条路径都拼得出来、≤20 字、无阿拉伯数字、无病名、无内部词
  const complaintLimit = db.text_limits.chief_complaint_max_chars
  const symptomSet = db.answers.chief_complaints.values
  const durationSet = db.answers.duration.values
  const complaints = []
  for (const s of [...symptomSet, { id: db.refuse.id, record: db.refuse.record }]) {
    for (const d of [...durationSet, { id: db.refuse.id, record: db.refuse.record }]) {
      const text = chiefComplaint(db, { answers: complaintOnly(db, s.id, d.id), signed: false })
      complaints.push({ symptom: s.id, duration: d.id, text })
      if (!text || !text.trim()) err('chief_complaint_unwritable', `${s.id} × ${d.id} 拼不出主诉`)
      if ([...text].length > complaintLimit) err('chief_complaint_too_long', `「${text}」${[...text].length} 字，超过 ${complaintLimit}`)
      if (db.text_limits.forbid_digits && /[0-9０-９]/.test(text)) err('chief_complaint_has_digits', `「${text}」含阿拉伯数字`)
      for (const name of diseases.items.map((x) => x.label)) {
        if (name && text.includes(name)) err('chief_complaint_names_diagnosis', `「${text}」含病名「${name}」`)
      }
      for (const w of internal) if (text.includes(w)) err('copy_leaks_internal', `主诉「${text}」含内部词「${w}」`)
    }
  }

  // 5. 拒答不锁死：每一种拒答都能把病历写完并签字
  //    只有闭集齐全的分支才枚举（闭集缺失时上面已经报过 question_without_closed_set，这里不重复崩）。
  const usableBranches = branchSummary(db).filter((branch) => {
    const ids = plan(db, { [db.questions.find((q) => q.answers === 'complaint').id]: branch.id })
    return ids.every((id) => optionsOf(db, questionById(db).get(id)).length > 1)
  })
  const refusalCases = []
  const selector = db.questions.find((q) => q.answers === 'complaint')
  for (const branch of usableBranches) {
    const full = {}
    for (const id of plan(db, { [selector.id]: branch.id })) full[id] = null
    const all = { ...full }
    for (const id of Object.keys(all)) all[id] = db.refuse.id
    refusalCases.push({ branch: branch.id, kind: 'all_refused', answers: all })
    for (const id of Object.keys(full)) {
      const one = { ...full }
      for (const other of Object.keys(one)) one[other] = db.refuse.id
      const q = questionById(db).get(id)
      one[id] = optionsOf(db, q).find((o) => o.id !== db.refuse.id).id
      refusalCases.push({ branch: branch.id, kind: `only_${id}_answered`, answers: one })
    }
  }
  for (const c of refusalCases) {
    let state = { answers: {}, signed: false }
    let guard = 0
    let question = currentQuestion(db, state)
    while (question && guard < 500) {
      const want = c.answers[question.id]
      const fallback = optionsOf(db, question)[0]
      if (!fallback) { err('refusal_locks_run', `${c.branch} / ${c.kind}：${question.id} 一档取值都没有`); break }
      state = applyAnswer(db, state, question.id, want ?? fallback.id).state
      guard += 1
      question = currentQuestion(db, state)
    }
    if (guard >= 500) err('refusal_locks_run', `${c.branch} / ${c.kind}：问诊推进不收敛`)
    if (!isComplete(db, state)) err('refusal_locks_run', `${c.branch} / ${c.kind}：拒答之后走不完`)
    if (!canSign(db, state)) err('refusal_locks_run', `${c.branch} / ${c.kind}：拒答之后签不了字`)
    const paper = paperColumns(db, state, { character: null, legacyCharacterSource: { identity: {} } })
    if (!paper.some((col) => col.id === 'historian_sign')) err('refusal_locks_run', `${c.branch} / ${c.kind}：纸上没有落款栏`)
    // 拼出来的病史必须是「整理过的句子」，不是「一问一行」的填表痕迹（阶段 6）。
    for (const col of paper) {
      if (!col.composed || !col.text) continue
      if (/[：:]/.test(col.text)) err('prose_reads_like_a_form', `${c.branch} / ${c.kind}：栏目「${col.label}」拼出来的字里有冒号`)
      if (!col.text.endsWith('。')) err('prose_without_full_stop', `${c.branch} / ${c.kind}：栏目「${col.label}」没有以句号收尾`)
    }
  }

  // 6. 语言指纹与拼句（阶段 6）：拼句引用到的每一档都要有临床片段；语言指纹必须登记过
  const voiceIds = new Set(voiceProfiles(db).map((v) => v.id))
  if (!voiceIds.size) err('voices_missing', '没有登记任何语言指纹')
  for (const id of voiceIds) {
    const profile = voiceById(db).get(id)
    if (!profile.screen_name) err('voice_without_screen_name', `语言指纹「${id}」没有上屏用的名字`)
    if (!(profile.basis ?? []).length) err('voice_without_basis', `语言指纹「${id}」没有依据`)
  }
  // 拼句模板引用到的问 = 要落到纸上的那些问：它们的每一档（拒答档除外）都必须有 clause。
  const composed = new Set(Object.values(db.compose ?? {})
    .flatMap((spec) => (spec.sentences ?? []).flatMap((sentence) => (sentence.parts ?? []).map((part) => part.q))))
  for (const q of db.questions) {
    if (q.ask_mode !== 'player') continue
    for (const v of answerSetOf(db, q)?.values ?? []) {
      if (v.voice && !voiceIds.has(v.voice)) err('voice_unknown', `${q.id} 的取值「${v.id}」打了不存在的语言指纹「${v.voice}」`)
      if (v.voice && v.label === (v.record ?? v.label)) warn('voice_without_voice', `${q.id} 的取值「${v.id}」打了语言指纹，但嘴上说的与纸上写的还是同一句`)
      if (!composed.has(q.id)) continue
      if (isRefuse(db, v.id)) continue
      const clause = v.clause
      if (!clause) { err('clause_missing', `${q.id} 的取值「${v.id}」要写上纸，却没有临床片段（clause）`); continue }
      if (db.text_limits.forbid_digits && /[0-9０-９]/.test(clause)) err('clause_has_digits', `${q.id}.${v.id} 的临床片段含阿拉伯数字：「${clause}」`)
      if (/(?<!自)我|咱/.test(clause)) err('clause_first_person', `${q.id}.${v.id} 的临床片段是第一人称：「${clause}」`)
      for (const w of internal) if (clause.includes(w)) err('copy_leaks_internal', `${q.id}.${v.id} 的临床片段含内部词「${w}」`)
      for (const name of diseases.items.map((d) => d.label)) {
        if (name && clause.includes(name)) err('clause_names_diagnosis', `${q.id}.${v.id} 的临床片段含病名「${name}」`)
      }
    }
  }
  const questionOf = questionById(db)
  for (const [columnId, spec] of Object.entries(db.compose ?? {})) {
    if (!columnIds.has(columnId)) err('compose_unknown_column', `拼句模板指向了不存在的栏目「${columnId}」`)
    for (const sentence of spec.sentences ?? []) {
      if (!sentence.basis) err('compose_without_basis', `栏目「${columnId}」的句子「${sentence.id}」没有依据`)
      if (!(sentence.parts ?? []).length) err('compose_empty_sentence', `栏目「${columnId}」的句子「${sentence.id}」一段都没有`)
      for (const part of sentence.parts ?? []) {
        const target = questionOf.get(part.q)
        if (!target) err('compose_unknown_question', `栏目「${columnId}」的句子引用了不存在的「${part.q}」`)
        else if (target.ask_mode !== 'player') err('compose_question_not_player', `栏目「${columnId}」的句子引用了玩家答不了的「${part.q}」`)
      }
    }
  }
  for (const col of db.record.columns) {
    // 只有「由许多问一起落笔」的那几栏才是整段病史；首页那几笔（姓名 / 性别 / 婚姻 / 过敏）各有取值来源。
    const prose = col.fill === 'patient_input' && !col.value_from_question && !col.value_from_source
    if (prose && !db.compose?.[col.id]) err('compose_missing_for_column', `栏目「${col.label}」是整段病史却没有拼句模板`)
  }
  for (const row of db.record.observations ?? []) {
    if (!row.derive) continue
    if (!['voice', 'answer'].includes(row.derive.from)) { err('observation_derive_unknown', `「${row.label}」的落笔来源「${row.derive.from}」不在词表里`); continue }
    if (row.derive.from === 'voice') {
      for (const id of voiceIds) if (!row.derive.table?.[id]) err('observation_voice_table_incomplete', `「${row.label}」缺语言指纹「${id}」的那一行写法`)
    }
    if (row.derive.from === 'answer') {
      const target = questionOf.get(row.derive.q)
      if (!target) { err('observation_derive_unknown', `「${row.label}」指向了不存在的「${row.derive.q}」`); continue }
      for (const key of Object.keys(row.derive.table ?? {})) {
        if (!answerSetOf(db, target)?.values.some((v) => v.id === key)) err('observation_derive_unknown', `「${row.label}」的表里有「${target.id}」答不出来的「${key}」`)
      }
    }
  }

  // 6. 一局问数上限
  const limit = 40
  for (const row of runCounts(db)) {
    const worst = Math.max(row.max, row.sampled_max)
    if (worst > limit) err('run_too_long', `${row.label}：一局最多 ${worst} 问，超过 ${limit} 问上限`)
    if (row.upper_bound_all_followups > limit) {
      warn('run_upper_bound_is_over_estimate', `${row.label}：把所有追问同时打开的过估值是 ${row.upper_bound_all_followups} 问（这些追问的触发条件互斥，实际走不到）`)
    }
  }

  // 7. 阶段 7：那件事 → 病 → 诊断栏（一条判据一个 id，报错都要能指到数据行）
  //
  //    这一段的判据分三组：
  //      a) 定位（数据在 db.event_wiring.locate + odb.events）——一局恰一件是**结构保证**，这里现场核；
  //      b) 事件包（数据在 odb.event_rule + odb.events）——扩展位、素材、属性效果、激活的病；
  //      c) 言语与落笔（数据在 db.voices + db.record.columns）——指纹挂病、诊断栏的笔迹。
  const wiring = db.event_wiring ?? null
  const eventList = odb.events ?? []
  const rule = odb.event_rule ?? {}
  const eventIds = new Set(eventList.map((e) => e.id))
  const facetSpec = odb.vocab ?? {}
  const attrIds = new Set(odb.attributes?.ids ?? [])
  const materialById = new Map((odb.experiences ?? []).map((e) => [e.id, e]))
  const roster = diseases.items.filter((i) => i.always_on !== true)
  const rosterIds = new Set(roster.map((i) => i.id))
  if (!wiring) err('event_wiring_missing', '没有 event_wiring：一局的经历接不回病历（阶段 7 的链条缺入口）')
  if (!eventList.length) err('events_missing', 'data/opening.json 里没有 events 块')

  // a) 定位
  const locate = wiring?.locate ?? null
  const dataMap = questionById(db)
  if (locate) {
    const fallback = locate.fallback_event
    if (!fallback || !eventIds.has(fallback)) err('event_locate_fallback_missing', `兜底事件「${fallback}」不存在：没有它就不能保证「一局恰一件」`)
    const reachable = new Set()
    for (const r of locate.rules ?? []) {
      const target = questionOf.get(r.q)
      if (!target) { err('locate_question_unknown', `${r.id} 指向了不存在的问「${r.q}」`); continue }
      const spec = answerSetOf(db, target)
      for (const v of r.in ?? []) {
        if (!spec?.values.some((x) => x.id === v)) err('locate_value_unknown', `${r.id}：${r.q} 的闭集里没有「${v}」`)
      }
      if (!eventIds.has(r.event)) err('locate_event_unknown', `${r.id} 指向了不存在的事件「${r.event}」`)
      else reachable.add(r.event)
    }
    if (fallback) reachable.add(fallback)
    for (const id of eventIds) if (!reachable.has(id)) err('event_unreachable', `事件「${id}」没有任何定位规则能到达它（死事件）`)

    // ★★ 症状闭集不许拿来筛事件（校准第 2 条）。两条判据：
    //    ① 规则只能问「发生过什么」——`q` 必须在 locate.experience_questions 白名单里；
    //    ② 措辞像事件、其实是症状（或不是经历）的那几档，'forbid' 的一律报错、'note' 的报警告。
    //    动机：`chief_complaints.anger`（症状：差点跟人吵起来）与 `event.conflict`（经历：冲突）
    //    措辞相同、语义不同轴——把它当筛子就是把因果方向反过来。本批定位**只用** q093 · q009 ·
    //    q086 · q074 · q043 五个问，一个症状问都没有。
    const experienceQs = new Set((locate.experience_questions ?? []).map((x) => x.q))
    const traps = locate.symptom_traps ?? []
    for (const r of locate.rules ?? []) {
      const target = dataMap.get(r.q)
      if (!experienceQs.has(r.q)) {
        err('locate_question_not_experience', `${r.id} 用了不在 experience_questions 白名单里的问「${r.q}」：定位只能问「发生过什么」，不许问「你现在什么症状」`)
      }
      const set = target?.answers ?? null
      for (const v of r.in ?? []) {
        const trap = traps.find((t) => t.answer_set === set && t.value_id === v)
        if (!trap) continue
        if (trap.severity === 'forbid') err('locate_uses_symptom_trap', `${r.id} 用了症状陷阱档 ${set}.${v}（看起来像 ${trap.looks_like}）：${trap.why}`)
        else warn('locate_uses_weak_discriminator', `${r.id} 用了弱判别档 ${set}.${v}：${trap.why}`)
      }
    }
    // one_event_per_run：枚举每个主诉分支的「每题 k 档 / 全部拒答」组合，核每个组合都定位得到事件
    for (const branch of branchSummary(db)) {
      const branchQ = plan(db, { [db.questions.find((q) => q.answers === 'complaint').id]: branch.id })
      const combos = []
      const maxOpts = Math.max(1, ...branchQ.map((id) => optionsOf(db, questionById(db).get(id)).length))
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
        const hit = (locate.rules ?? []).find((r) => locateRuleMatches(r, answers))
        const picked = hit ? hit.event : fallback
        if (!picked || !eventIds.has(picked)) err('one_event_per_run', `${branch.id}：某个答案组合下定位不到事件`)
      }
    }
  }

  // b) 事件包
  const activatesByDisease = new Map()
  for (const event of eventList) {
    const acts = event.activates ?? []
    if (!acts.length) err('event_activates_empty', `事件「${event.id}」一张病都没激活（死事件）`)
    if (acts.length < (rule.activates_min ?? 1) || acts.length > (rule.activates_max ?? 4)) {
      err('event_activates_range', `事件「${event.id}」激活 ${acts.length} 张病，超出 ${rule.activates_min ?? 1}–${rule.activates_max ?? 4}`)
    }
    if (new Set(acts).size !== acts.length) err('event_activates_duplicate', `事件「${event.id}」的 activates 里有重复`)
    for (const id of acts) {
      const d = diseases.items.find((x) => x.id === id)
      if (!d) err('event_activates_unknown', `事件「${event.id}」激活了不存在的病「${id}」`)
      else if (d.always_on === true) err('event_activates_always_on', `事件「${event.id}」激活了固有项「${id}」（不占额度、不进候选、不算名册）`)
      else activatesByDisease.set(id, (activatesByDisease.get(id) ?? 0) + 1)
    }
    // 每件事激活的病必须分属各不相同的语言指纹（否则「调子定下来之后收窄到 1 张」不成立）
    const voiced = acts.map((id) => voiceOfDisease(db, id))
    if (voiced.some((v) => !v)) {
      err('candidate_without_voice', `事件「${event.id}」激活的病里有没人代言的：${acts.filter((id) => !voiceOfDisease(db, id)).join(' / ')}`)
    } else if (new Set(voiced.map((v) => v.id)).size !== voiced.length) {
      err('event_voice_per_event', `事件「${event.id}」的 ${acts.length} 张病没有分属各不相同的语言指纹（调子与候选的一致性就不能保证）`)
    }

    // 扩展位
    const seen = new Set()
    const axes = new Set()
    for (const x of event.expansions ?? []) {
      if (seen.has(x.id)) err('expansion_duplicate', `事件「${event.id}」的扩展位「${x.id}」重复`)
      seen.add(x.id)
      if (!facetSpec[x.facet]) err('event_facet_unknown', `扩展位「${x.id}」的 facet「${x.facet}」不在 11 facet 词表里（不许新增轴）`)
      else if (!facetSpec[x.facet].values.some((v) => v.id === x.value)) err('event_facet_value_unknown', `扩展位「${x.id}」的取值「${x.value}」不在 ${x.facet} 的闭集里`)
      axes.add(x.facet)
      const target = questionOf.get(x.q)
      if (!target) { err('expansion_question_unknown', `扩展位「${x.id}」指向了不存在的问「${x.q}」`); continue }
      const opt = optionOf(db, target, x.value_id)
      if (!opt) { err('expansion_source_missing', `扩展位「${x.id}」：${x.q} 的闭集里没有「${x.value_id}」`); continue }
      if (x.label !== opt.label) err('expansion_label_mismatch', `扩展位「${x.id}」的 label 与 ${x.q}.${x.value_id} 的 label 不一致（重述漂了）`)
      const clause = opt.clause ?? opt.record ?? opt.label
      if (x.clause !== clause) err('expansion_clause_mismatch', `扩展位「${x.id}」的 clause 与 ${x.q}.${x.value_id} 的临床片段不一致（重述漂了）`)
      if (x.column !== target.column) err('expansion_column_mismatch', `扩展位「${x.id}」的 column 与 ${x.q} 落笔的栏目不一致`)
      // ★★ 不许按 id 跨文件认语义（校准第 4 条）：`value_id` 是 opening_clinic 的答案取值、
      //    `value` 是 opening 的词表取值，两者只是这一次显式映射的两端。恰好同名时必须留下交代。
      if (x.value_id === x.value && !x.same_id_note) {
        err('expansion_id_collision_unjustified', `扩展位「${x.id}」的两端 id 同名（${x.value_id}）却没写 same_id_note：两套数据有 10 个 id 撞名（none 一个 id 在 clinic 侧被 11 个语义不同的闭集共用），同名是巧合不是语义相等`)
      }
      // 答了必须上纸：这一问必须被某个拼句模板引用到
      if (!composed.has(x.q)) err('expand_not_on_paper', `扩展位「${x.id}」的问「${x.q}」不在任何拼句模板里：答了只出现在对话里，纸上没有`)
      for (const id of x.exclude ?? []) {
        if (!rosterIds.has(id)) err('expansion_exclude_unknown', `扩展位「${x.id}」排除了不在名册里的「${id}」`)
        if (!acts.includes(id)) warn('expansion_exclude_noop', `扩展位「${x.id}」排除了「${id}」，但它本来就不在这件事的 activates 里（不会改变任何一局）`)
      }
    }
    const min = rule.expansions_min ?? 0
    if ((event.expansions ?? []).length < min) err('event_expansion_thin', `事件「${event.id}」只有 ${(event.expansions ?? []).length} 个扩展位，低于下限 ${min}`)
    for (const axis of rule.expansion_axes_required ?? []) {
      if (!axes.has(axis)) err('event_expansion_axis_missing', `事件「${event.id}」的扩展位没有覆盖「${axis}」这一位`)
    }
    // 素材
    const mats = event.source_experiences ?? []
    if (mats.length < (rule.material_min ?? 0) || mats.length > (rule.material_max ?? Infinity)) {
      err('event_material_count', `事件「${event.id}」有 ${mats.length} 段素材，超出 ${rule.material_min}–${rule.material_max}`)
    }
    const sum = {}
    for (const id of mats) {
      const rec = materialById.get(id)
      if (!rec) { err('event_material_dead', `事件「${event.id}」的素材「${id}」不存在`); continue }
      if (!(rec.diseases ?? []).some((d) => acts.includes(d))) {
        err('event_material_not_activating', `事件「${event.id}」的素材「${id}」指向的病与它的 activates 不相交（扩写关系不成立）`)
      }
      for (const [k, v] of Object.entries(rec.effects?.attributes ?? {})) sum[k] = (sum[k] ?? 0) + v
    }
    // 属性效果：必须是素材的合计（一个数，不是两个）
    const eff = event.effects?.attributes ?? {}
    const keys = [...new Set([...Object.keys(sum), ...Object.keys(eff)])].sort()
    if (keys.some((k) => (sum[k] ?? 0) !== (eff[k] ?? 0))) {
      err('event_effects_not_from_material', `事件「${event.id}」的 effects 与它的素材合计不一致：素材 ${JSON.stringify(sum)} vs 事件 ${JSON.stringify(eff)}`)
    }
    if (Object.keys(eff).length > (rule.effects_terms_max ?? 2)) err('event_effects_terms', `事件「${event.id}」的 effects 有 ${Object.keys(eff).length} 项，超过 ${rule.effects_terms_max}`)
    for (const k of Object.keys(eff)) if (!attrIds.has(k)) err('event_effects_unknown_attribute', `事件「${event.id}」的 effects 里有不存在的属性「${k}」`)

    // 那件事本身
    if (!event.claim) err('event_without_claim', `事件「${event.id}」没有 claim（「这件事打乱了他人生轨迹的哪一段」）`)
    for (const [field, max] of [['title', odb.text_lint?.title_max], ['summary', odb.text_lint?.summary_max]]) {
      const text = event[field]
      if (!text) { err('event_without_text', `事件「${event.id}」没有 ${field}`); continue }
      if (max && [...text].length > max) err('event_text_too_long', `事件「${event.id}」的 ${field}${[...text].length} 字，超过 ${max}`)
      if (odb.text_lint?.forbid_digits && /[0-9０-９]/.test(text)) err('event_text_has_digit', `事件「${event.id}」的 ${field}含数字：「${text}」`)
      for (const w of odb.text_lint?.extra_banned ?? []) if (text.includes(w)) err('event_text_banned_word', `事件「${event.id}」的 ${field}含禁词「${w}」`)
      for (const f of odb.text_lint?.from_label_facets ?? []) {
        for (const v of odb.vocab?.[f]?.values ?? []) if (text.includes(v.label)) err('event_text_leaks_facet_label', `事件「${event.id}」的 ${field}含 ${f} 的标签「${v.label}」`)
      }
    }
    for (const [axis, spec] of Object.entries(event.spine ?? {})) {
      if (!facetSpec[axis]) { err('event_spine_facet_unknown', `事件「${event.id}」的 spine 里有不存在的 facet「${axis}」`); continue }
      for (const v of Array.isArray(spec) ? spec : [spec]) {
        if (!facetSpec[axis].values.some((x) => x.id === v)) err('event_spine_value_unknown', `事件「${event.id}」的 spine.${axis} 取值「${v}」不在闭集里`)
      }
    }
  }

  // 病覆盖：名册每张至少被一件事激活
  const coveredCount = rosterIds.size ? [...rosterIds].filter((id) => activatesByDisease.has(id)).length : 0
  const target = rule.coverage?.target_this_batch ?? 6
  if (coveredCount < target) err('event_coverage', `病覆盖只有 ${coveredCount} 张，低于本批目标 ${target}`)
  const dead = [...rosterIds].filter((id) => !activatesByDisease.has(id))
  if (dead.length) warn('event_coverage_gap', `${dead.length} 张名册病还没有任何事件激活：${dead.join(' / ')}`)

  // c) 言语与落笔
  const diagnosisColumn = db.record.columns.find((c) => c.id === 'diagnosis')
  if (!diagnosisColumn) err('diagnosis_column_missing', '纸上没有「诊断」这一栏')
  else {
    if (diagnosisColumn.who !== 'hospital') err('diagnosis_pen_not_hospital', `诊断栏的 who 是「${diagnosisColumn.who}」，必须是 hospital（玩家只做「认」，落笔的是医师）`)
    if (diagnosisColumn.fill !== 'derived') err('diagnosis_pen_not_hospital', `诊断栏的 fill 是「${diagnosisColumn.fill}」，必须是 derived`)
    if (diagnosisColumn.value_from !== 'confirmed_disease') err('diagnosis_source_unknown', `诊断栏的 value_from 是「${diagnosisColumn.value_from}」，必须是 confirmed_disease`)
  }
  const treatmentColumn = db.record.columns.find((c) => c.id === 'treatment')
  if (treatmentColumn && treatmentColumn.fill !== 'blank') warn('treatment_written_early', `治疗意见栏的 fill 是「${treatmentColumn.fill}」——owner 待裁 3 的默认是仍留白（医嘱尚无口径）`)
  const voicedNow = new Set()
  for (const profile of voiceProfiles(db)) {
    if (!profile.disease) err('voice_without_disease', `语言指纹「${profile.id}」没有挂病（阶段 7 起指纹挂在病上）`)
    else if (!diseases.items.some((d) => d.id === profile.disease)) err('voice_disease_unknown', `语言指纹「${profile.id}」挂的病「${profile.disease}」不存在`)
    for (const id of [profile.disease, ...(profile.covers ?? [])]) if (id) voicedNow.add(id)
  }
  for (const id of activatesByDisease.keys()) {
    if (!voicedNow.has(id)) err('candidate_without_voice', `被事件激活的病「${id}」没有任何语言指纹代言：候选里有它，但这一局没有台词特征`)
  }

  // 一局的候选数分布 + 调子一致性（按每个分支的「每题 k 档 / 全部拒答」枚举）
  const candidateHistogram = {}
  let voiceMismatch = 0
  const selectorQ = db.questions.find((q) => q.answers === 'complaint')
  for (const branch of branchSummary(db)) {
    const branchQ = plan(db, { [selectorQ.id]: branch.id })
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
      const state = { answers, signed: false, disease: null }
      const { candidates } = eventDiseaseCandidates(db, odb, diseases, state)
      candidateHistogram[candidates.length] = (candidateHistogram[candidates.length] ?? 0) + 1
      if (candidates.length > (rule.candidate_max ?? 4)) err('candidate_over_limit', `${branch.id}：候选 ${candidates.length} 张，超过上界 ${rule.candidate_max}`)
      if (candidates.length === 0) err('candidate_empty', `${branch.id}：某个答案组合下候选一张都没有（患者意见栏会空着）`)
      const { dominant } = voiceTally(db, state)
      if (dominant) {
        if (candidates.length !== 1) {
          voiceMismatch += 1
          err('voice_disease_conflict', `${branch.id}：调子已显出（${dominant}）但候选有 ${candidates.length} 张`)
        } else if (voiceOfDisease(db, candidates[0].id)?.id !== dominant) {
          voiceMismatch += 1
          err('voice_disease_conflict', `${branch.id}：认下的「${candidates[0].id}」与调子「${dominant}」不一致`)
        }
      }
    }
  }
  // 全拒答那一局：仍能定位事件，且诊断栏仍是空白态（没认就不许落笔）
  for (const branch of branchSummary(db)) {
    const branchQ = plan(db, { [selectorQ.id]: branch.id })
    const answers = { [selectorQ.id]: branch.id }
    for (const id of branchQ) if (id !== selectorQ.id) answers[id] = db.refuse.id
    const state = { answers, signed: true, disease: null }
    if (!seedEvent(db, odb, answers).event) err('one_event_per_run', `${branch.id}（全拒答）：定位不到事件`)
    const paper = paperColumns(db, state, { character: null, legacyCharacterSource: { identity: {} }, openingDb: odb, diseases })
    const diag = paper.find((c) => c.id === 'diagnosis')
    if (!diag) err('diagnosis_column_missing', `${branch.id}（全拒答）：纸上没有诊断栏`)
    else if (diag.resolved) err('diagnosis_pen_not_hospital', `${branch.id}（全拒答）：还没认病，诊断栏却已经落笔了`)
  }

  // 素材台账：被用到的 / 永不被任何事件用到的（**只报数，不报错**——owner 待裁 7 的默认 (a)）
  const usedMaterials = new Set(eventList.flatMap((e) => e.source_experiences ?? []))

  return {
    errors,
    warnings,
    numbers: {
      questions: db.questions.length,
      modes: mode,
      required: requiredQuestions(db).length,
      sensitive: db.questions.filter((q) => q.sensitive).length,
      columns: db.record.columns.length,
      answer_sets: Object.keys(db.answers).length,
      branches: branchSummary(db).length,
      complaint_paths: complaints.length,
      refusal_cases: refusalCases.length,
      voices: voiceIds.size,
      voiced_values: db.questions.reduce((sum, q) => (q.ask_mode === 'player'
        ? sum + (answerSetOf(db, q)?.values ?? []).filter((v) => v.voice).length : sum), 0),
      clauses: db.questions.reduce((sum, q) => (q.ask_mode === 'player'
        ? sum + (answerSetOf(db, q)?.values ?? []).filter((v) => v.clause).length : sum), 0),
      compose_sentences: Object.values(db.compose ?? {}).reduce((sum, spec) => sum + (spec.sentences ?? []).length, 0),
      runs: runCounts(db),
      // ── 阶段 7 的报数（提示词 §十一 点名要的那一组）──────────────────────
      events: eventList.length,
      locate_rules: (locate?.rules ?? []).length,
      locate_fallback: locate?.fallback_event ?? null,
      event_diseases_covered: coveredCount,
      roster: rosterIds.size,
      event_expansions: eventList.map((e) => ({ id: e.id, expansions: (e.expansions ?? []).length })),
      event_activates: eventList.map((e) => ({ id: e.id, activates: (e.activates ?? []).length })),
      candidates: candidateHistogram,
      voice_mismatch_runs: voiceMismatch,
      material: {
        total: (odb.experiences ?? []).length,
        used: usedMaterials.size,
        unused: (odb.experiences ?? []).length - usedMaterials.size,
      },
    },
  }
}
