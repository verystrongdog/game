/**
 * 开局：**一张病历单 + 贴着纸的问诊条**（Web 原型）。
 *
 * 形态（owner 2026-09-27 五条裁定，见 design/presentation/开局病历填报.md §十三）：
 *   - 一屏一张纸：纸上按法定栏目顺序排着一般情况 / 主诉 / 现病史 / 既往史 / 个人史 /
 *     家族史 / 专科情况 / 初步诊断 / 患者意见 / 落款，**没有五屏步条、没有卡片网格、
 *     没有右侧统计栏**。正在填的那一栏高亮，已填的栏目显示文字，没填的显示自己的空白态。
 *   - 一问一答：**患者先自述疾病**（第 1 问），病历撰写人再在贴着纸的问诊条上问一句，
 *     玩家在闭集里答一句，答案当场写成纸上的字，然后自动进下一问；答完八问才开始核对
 *     既往史里的条目（owner 2026-09-27 裁定，见 design/presentation/开局病历填报.md §十四）。
 *   - 主题红线：**你无法选择出现什么，只能选择怎么面对。** 记录由院方写、玩家只提供陈述；
 *     玩家只有三种笔：**答 · 认 · 签**——纸上的每一笔要么由他答（闭集），要么由他认
 *     （池子里的条目逐条「以上属实」），要么由他签（落款）。他不能填、不能改、不能挑。
 *
 * 全部栏目名、问法、答案取值与按钮文案都从 `data/opening.json` 读；本文件只留状态提示语。
 * 池子口径（哪几问参与相符判断、放宽阶梯、池子的下限）由 `opening.js` 现算，这里不复制判据。
 *
 * 边界（AGENTS.md §二 拦截规则）：只服务开局 / Web 演示，不得引入 C# 引擎或
 * 神经模拟系统的任何概念；战斗相关内容一律不碰。
 *
 * 数据权威：`data/opening.json`（经历与病历单）与 `data/diseases.json`（疾病）。
 *
 * 🔧 **阶段 5（2026-09-27）：开局入口已切到 `web/src/opening-clinic/`，本模块不再被调用**；
 * 它连同 `data/opening.json` 的阶段 4 契约原样保留、待接回。现行口径见
 * `design/presentation/开局门诊问诊.md`。
 */

import db from '../../../data/opening.json'
import ddb from '../../../data/diseases.json'
import { attributeDescriptions } from './attribute-copy.js'
import { developmentDefaultCharacter } from './dev-default.js'
import {
  characterFieldOf,
  characterFor,
  characterOptions,
  characterSources,
  complaintText,
  composeName,
  defaultSourceId,
  recordRows,
} from './character-source.js'
import {
  answerChoices,
  answerText,
  byId,
  canSelect,
  describe as describeExperience,
  diseaseCandidates,
  interviewPool,
  interviewQuestions,
  isAnswered,
  questionById,
  settleAttributes,
} from './opening.js'
import { describeDisease, diseaseCanStillPick } from './diseases.js'

const recordShell = db.record_shell
const paperSpec = recordShell.paper
const interview = db.interview
const sourceSpec = db.character_source
const attrIds = db.attributes.ids

const escapeHtml = (value) => String(value)
  .replaceAll('&', '&amp;')
  .replaceAll('<', '&lt;')
  .replaceAll('>', '&gt;')
  .replaceAll('"', '&quot;')

/** 某一栏（按 `from` 找）——栏目名只在数据里说一次，这里按来源键取。 */
const columnWith = (from) => paperSpec.columns.find((c) => (c.writes ?? []).some((w) => w.from === from))
const columnById = (id) => paperSpec.columns.find((c) => c.id === id)

export function createCharacterCreation({ trigger, required = false }) {
  const profileListeners = new Set()
  const state = {
    open: false,
    /** 八问的答案：答案轴 → 取值 id（多值问是数组；`[]` 表示「一个人」，仍是答过了）。 */
    answers: {},
    /** 问诊条停在第几问；答满八问后不再前进。 */
    cursor: 0,
    /** 同一张纸上的四个阶段：问诊 · 核对既往史 · 患者意见 · 落款。 */
    stage: 'interview',
    /** 已核对属实的条目（必须落在本局的池子里）。 */
    confirmed: new Set(),
    characterSource: defaultSourceId(db),
    surname: null,
    given: null,
    gender: null,
    selectedDiseases: new Set(),
    message: '',
    completed: false,
  }

  const root = document.createElement('div')
  root.className = 'cc-overlay'
  root.hidden = true
  root.innerHTML = '<section class="cc-shell" role="dialog" aria-modal="true" aria-labelledby="ccTitle"></section>'
  document.body.append(root)
  const shell = root.querySelector('.cc-shell')

  // ── 派生状态（一律现算，不存在第二份） ────────────────────────────────
  const selectedIds = () => [...state.confirmed]
  const settlement = () => settleAttributes(db, selectedIds())
  const candidates = () => diseaseCandidates(db, ddb, selectedIds())
  const remaining = () => db.quota.total - state.confirmed.size
  const answeredCount = () => interviewQuestions(db).filter((q) => isAnswered(state.answers, q.facet)).length
  const currentQuestion = () => interviewQuestions(db)[state.cursor] ?? null

  /**
   * 本局的池子：由八问里参与相符判断的那三问（病前经历）现算（放宽阶梯在 opening.js 里）。
   * 缓存键只看那三问——自述与时间三问换答案不换池子。
   */
  let poolCache = { key: null, value: null }
  function pool() {
    const key = JSON.stringify(interviewQuestions(db).filter((q) => q.matches === true)
      .map((q) => [q.facet, state.answers[q.facet] ?? null]))
    if (poolCache.key !== key) poolCache = { key, value: interviewPool(db, ddb, state.answers) }
    return poolCache.value
  }
  const poolIds = () => pool().ids

  /** 改答案 = 换池子：新池子里没有的条目必须退回未核对。 */
  function reconcileExperiences() {
    const allowed = new Set(poolIds())
    for (const id of state.confirmed) if (!allowed.has(id)) state.confirmed.delete(id)
    reconcileDiseases()
  }

  function reconcileDiseases() {
    const allowed = new Set(candidates().map((d) => d.id))
    for (const id of state.selectedDiseases) if (!allowed.has(id)) state.selectedDiseases.delete(id)
  }

  /**
   * 这一份记录写给谁。
   *
   * ⚠️ 人物来源**不参与**问诊、配额与疾病候选：它只决定页眉那两笔怎么念，
   * 所以换人物不清空任何东西。
   */
  function character() {
    return characterFor(db, {
      source: state.characterSource,
      name: state.surname && state.given ? `${state.surname}${state.given}` : null,
      gender: state.gender,
    })
  }

  const isCustom = () => state.characterSource === 'custom'

  function profile() {
    const who = character()
    return {
      id: 'character_creation',
      label: '开局人物',
      experiences: [...state.confirmed],
      diseases: [...state.selectedDiseases],
      source: who.source,
      ...(who.name ? { name: who.name } : {}),
      ...(who.gender ? { gender: who.gender } : {}),
    }
  }

  function notifyProfile() {
    const value = profile()
    profileListeners.forEach((listener) => listener(value))
  }

  // ── 纸上的一笔写成什么 ───────────────────────────────────────────────
  const diseaseLabel = (id) => ddb.items.find((d) => d.id === id)?.label ?? id

  function blankOf(write) {
    if (!write.blank_from) return write.blank ?? ''
    const [block, key] = write.blank_from.split('.')
    return db[block]?.[key] ?? ''
  }

  /** 某一笔现在写成了什么：`{text, resolved}`——没答的显示自己的空白态。 */
  function writeText(write) {
    const q = questionById(db, write.from)
    if (q) {
      if (!isAnswered(state.answers, q.facet)) return { text: write.blank ?? '', resolved: false }
      return { text: answerText(db, q, state.answers[q.facet]), resolved: true }
    }
    if (write.from === 'complaint') {
      const text = complaintText(db, state.answers)
      return text ? { text, resolved: true } : { text: blankOf(write), resolved: false }
    }
    if (write.from === 'attributes') {
      if (!state.confirmed.size) return { text: write.blank ?? '', resolved: false }
      const s = settlement()
      return {
        text: attrIds.map((k) => `${db.attributes.labels[k]} ${s.band[k].label}`).join(' · '),
        resolved: true,
      }
    }
    if (write.from === 'sign') {
      // 经治医师那一笔法定必签；病史陈述者那一笔等玩家签字。
      if (write.fill === 'patient_input') {
        return state.completed
          ? { text: recordShell.sign.signed, resolved: true }
          : { text: recordShell.sign.unsigned, resolved: false }
      }
      return { text: recordShell.sign.signed, resolved: true }
    }
    return { text: write.blank ?? '', resolved: false }
  }

  /** 正在填的是哪一笔：问诊阶段＝当前那一问；其余阶段＝池子 / 意见 / 落款。 */
  function activeFrom() {
    if (state.stage === 'interview') return currentQuestion()?.id ?? null
    if (state.stage === 'confirm') return 'pool'
    if (state.stage === 'opinion') return 'opinion'
    return 'sign'
  }

  // ── 页眉：一般情况（只读 + 两笔可填） ────────────────────────────────
  function recordHeader() {
    const char = character()
    const rows = recordRows(db, char, state.answers)
    const who = sourceSpec.ui
    const pickable = characterFieldOf(db, { label: '姓名' })
    return `
      <div class="cc-record-head">
        <dl>${rows.map((r) => `
          <div class="cc-record-row ${r.who}${r.composite ? ' composite' : ''}">
            <dt>${escapeHtml(r.label)}</dt>
            ${r.composite
              ? `<dd>${r.from.label ? `<i>${escapeHtml(r.from.label)}</i>` : ''}<span class="cc-ink-${r.from.resolved ? 'patient' : 'blank'}">${escapeHtml(r.from.text)}</span>
                 <i>${escapeHtml(recordShell.ink.hospital)}</i><span class="cc-ink-hospital">${escapeHtml(r.lockedTo.text)}</span></dd>`
              : `<dd class="cc-ink-${r.who}${r.resolved ? '' : ' blank'}">${escapeHtml(r.text)}</dd>`}
          </div>`).join('')}</dl>
        <div class="cc-character">
          <span class="cc-character-label">${escapeHtml(who.label)}</span>
          ${Object.entries(characterSources(db))
            .map(([key, spec]) => `
              <button type="button" class="cc-character-option${(key === 'custom') === isCustom() ? ' active' : ''}"
                data-character-source="${escapeHtml(key)}">${escapeHtml(spec.label)}</button>`).join('')}
          ${isCustom() ? characterPicker(pickable) : `<span class="cc-character-note">${escapeHtml(who.note)}</span>`}
        </div>
      </div>`
  }

  /** 自建人物的闭集选择件：**没有输入框**，取值全部来自数据。 */
  function characterPicker(field) {
    const opts = characterOptions(db)
    const chip = (group, value, chosen) => `
      <button type="button" class="cc-name-chip${chosen === value ? ' active' : ''}"
        data-character-field="${escapeHtml(group)}" data-value="${escapeHtml(value)}"
        aria-pressed="${chosen === value}">${escapeHtml(value)}</button>`
    return `
      <div class="cc-name-picker">
        <span class="cc-character-label">${escapeHtml(field?.label ?? opts.name.label)}</span>
        <div class="cc-name-group"><i>${escapeHtml(opts.name.surname.label)}</i>
          ${opts.name.surname.values.map((v) => chip('surname', v, state.surname)).join('')}</div>
        <div class="cc-name-group"><i>${escapeHtml(opts.name.given.label)}</i>
          ${opts.name.given.values.map((v) => chip('given', v, state.given)).join('')}</div>
        <span class="cc-character-label">${escapeHtml(opts.gender.label)}</span>
        <div class="cc-name-group">${opts.gender.values.map((v) => `
          <button type="button" class="cc-name-chip${state.gender === v.id ? ' active' : ''}"
            data-character-field="gender" data-value="${escapeHtml(v.id)}"
            aria-pressed="${state.gender === v.id}">${escapeHtml(v.label)}</button>`).join('')}</div>
      </div>`
  }

  // ── 纸上的一笔 ───────────────────────────────────────────────────────
  /** 笔的名字与栏名一样时不再重复写一遍（主诉 / 患者意见这种栏名即笔名的栏目）。 */
  const labelSpan = (col, write) => (write.label === col.label
    ? ''
    : `<span class="cc-write-label">${escapeHtml(write.label)}</span>`)

  function writeRow(col, write) {
    const q = questionById(db, write.from)
    const { text, resolved } = writeText(write)
    const active = q && state.stage === 'interview' && currentQuestion()?.id === q.id
    // 这一笔是「玩家答出来的」还是「由答案现算的」——只影响样式（主诉那一行要写成成品的样子）。
    // 判据仍是数据里的 `from`：指得到一问的就是答出来的那一种。
    const kind = q ? 'answer' : 'source'
    return `
      <div class="cc-write cc-ink-${write.who}${resolved ? '' : ' cc-blank'}${active ? ' cc-write-active' : ''}"
        data-write="${escapeHtml(write.from)}" data-write-kind="${kind}">
        ${labelSpan(col, write)}
        <span class="cc-write-text">${escapeHtml(text)}</span>
        ${q && isAnswered(state.answers, q.facet)
          ? `<button type="button" class="cc-reanswer" data-reanswer="${escapeHtml(q.id)}">${escapeHtml(interview.reanswer)}</button>`
          : ''}
      </div>`
  }

  function blockReasonText(reasons) {
    return reasons.map((r) => {
      if (r.code === 'quota_value_full') return `「${r.label}」已经认满 ${r.max} 条`
      if (r.code === 'quota_total_full') return `已经认满 ${db.quota.total} 条`
      if (r.code === 'not_in_pool') return '这一条不在筛出来的池子里'
      if (r.code === 'would_deadlock') return '再认这一条就凑不满十段了'
      return r.code
    }).join('；')
  }

  /** 既往史：本局池子里的条目，逐条「以上属实」。 */
  function pastBody(col) {
    const write = col.writes[0]
    if (state.stage === 'interview') {
      return `<p class="cc-pool-note">${escapeHtml(interview.screen.pool_note)}</p>
        <div class="cc-write cc-ink-${write.who} cc-blank">${labelSpan(col, write)}<span class="cc-write-text">${escapeHtml(write.blank)}</span></div>`
    }
    const p = pool()
    return `
      <p class="cc-pool-count"><b>${state.confirmed.size}</b> / ${db.quota.total} · ${escapeHtml(interview.screen.pool_title)}</p>
      <p class="cc-pool-note">${escapeHtml(interview.screen.pool_note)}</p>
      <ol class="cc-pool-list">
        ${p.records.map((rec) => {
          const on = state.confirmed.has(rec.id)
          const verdict = canSelect(db, selectedIds(), rec.id, p.ids)
          const shape = describeExperience(db, rec.id)
          return `<li class="cc-pool-entry${on ? ' on' : ''}">
            <button type="button" class="cc-pool-item${on ? ' on' : ''}${verdict.ok || on ? '' : ' blocked'}"
              data-entry="${escapeHtml(rec.id)}" aria-pressed="${on}" aria-disabled="${!verdict.ok && !on}">
              <b>${escapeHtml(rec.title)}</b>
              <span class="cc-pool-summary">${escapeHtml(rec.summary)}</span>
              <small>${shape.facets.filter((f) => f.values.length)
                .map((f) => `${escapeHtml(f.name)}·${escapeHtml(f.values.join('/'))}`).join(' ｜ ')}</small>
              <small>留下了 · ${escapeHtml(shape.channels.join(' · '))}</small>
              <i class="cc-pool-verdict">${on ? escapeHtml(interview.screen.pool_confirm) : ''}</i>
            </button>
            ${verdict.ok || on ? '' : `<span class="cc-pool-blocked">${escapeHtml(blockReasonText(verdict.reasons))}</span>`}
          </li>`
        }).join('')}
      </ol>
      <small class="cc-write-note">${escapeHtml(col.basis)}</small>`
  }

  /** 病前能力与功能（院方评定，只读）。 */
  function attributeBody(write) {
    const s = settlement()
    return `
      <div class="cc-write cc-ink-hospital${state.confirmed.size ? '' : ' cc-blank'}">
        <span class="cc-write-label">${escapeHtml(write.label)}</span>
        ${state.confirmed.size
          ? `<div class="cc-attr-grid">${attrIds.map((k) => `
              <div class="cc-attr"><span>${escapeHtml(db.attributes.labels[k])}</span>
                <b>${escapeHtml(s.band[k].label)}</b>
                <i style="--level:${s.clamped[k]}"></i>
                <small>${escapeHtml(attributeDescriptions[k][s.band[k].id])}</small>
              </div>`).join('')}</div>`
          : `<span class="cc-write-text">${escapeHtml(write.blank)}</span>`}
        <small class="cc-write-note">${escapeHtml(write.note ?? '')}</small>
      </div>`
  }

  /** 专科情况：每条候选的诊断依据（院方写）。 */
  function basisBody(write) {
    const cands = candidates()
    if (!cands.length) {
      return `<div class="cc-write cc-ink-hospital cc-blank">
        ${labelSpan(columnWith('candidate_basis'), write)}
        <span class="cc-write-text">${escapeHtml(write.blank)}</span></div>`
    }
    return `
      <div class="cc-write cc-ink-hospital">
        ${labelSpan(columnWith('candidate_basis'), write)}
        <ul class="cc-basis-list">${cands.map((d) => `
          <li><b>${escapeHtml(diseaseLabel(d.id))}</b>
            <span>${escapeHtml(d.from.map((id) => byId(db, id).title).join(' · '))}</span></li>`).join('')}</ul>
      </div>`
  }

  /** 初步诊断：可能性较大的诊断（院方写）。 */
  function diagnosisBody(write) {
    const cands = candidates()
    if (!cands.length) {
      return `<div class="cc-write cc-ink-hospital cc-blank">
        ${labelSpan(columnWith('candidates'), write)}
        <span class="cc-write-text">${escapeHtml(write.blank)}</span></div>`
    }
    return `
      <div class="cc-write cc-ink-hospital">
        ${labelSpan(columnWith('candidates'), write)}
        <ul class="cc-diagnosis-list">${cands.map((d) => `
          <li>${escapeHtml(diseaseLabel(d.id))}</li>`).join('')}</ul>
      </div>`
  }

  /** 患者意见：在已列出的诊断上逐条表态（认 / 不认）。 */
  function opinionBody(col, write) {
    const cands = candidates()
    if (!cands.length) {
      return `<div class="cc-write cc-ink-patient cc-blank">
        ${labelSpan(col, write)}
        <span class="cc-write-text">${escapeHtml(write.blank)}</span></div>`
    }
    return `
      <div class="cc-write cc-ink-patient">
        ${labelSpan(col, write)}
        <div class="cc-opinion-list">${cands.map((c) => {
          const on = state.selectedDiseases.has(c.id)
          const verdict = diseaseCanStillPick(db, ddb, selectedIds(), c.id)
          return `<button type="button" class="cc-opinion${on ? ' on' : ''}${verdict.ok || on ? '' : ' blocked'}"
            data-disease="${escapeHtml(c.id)}" aria-pressed="${on}" aria-disabled="${!verdict.ok && !on}">
            ${escapeHtml(diseaseLabel(c.id))}
            <i>${on ? escapeHtml(write.actions.picked) : escapeHtml(write.actions.pick)}</i>
          </button>`
        }).join('')}</div>
        <small class="cc-write-note">${escapeHtml(col.basis)}</small>
      </div>`
  }

  /** 落款：经治医师已签 · 病史陈述者待签。 */
  function signBody(col) {
    return `
      <div class="cc-sign">
        ${col.writes.map((w) => {
          const { text, resolved } = writeText(w)
          return `<div class="${resolved ? 'signed' : 'unsigned'}">
            <span>${escapeHtml(w.label)}</span><b>${escapeHtml(text)}</b></div>`
        }).join('')}
        <small>${escapeHtml(recordShell.sign.pending)}</small>
      </div>
      <small class="cc-write-note">${escapeHtml(col.note ?? '')}</small>
      <small class="cc-write-note">${escapeHtml(col.detail ?? '')}</small>`
  }

  /**
   * 一栏的正文：每一笔按 `from` 分发。**代码里只认 `from` 这个来源键**，
   * 栏目名与每一笔的名字全部来自数据。
   */
  function columnBody(col) {
    if (col.writes_ref === 'general') return recordHeader()
    const writes = col.writes ?? []
    if (writes.some((w) => w.from === 'pool')) return pastBody(col)
    const parts = writes.map((w) => {
      if (w.from === 'attributes') return attributeBody(w)
      if (w.from === 'candidate_basis') return basisBody(w)
      if (w.from === 'candidates') return diagnosisBody(w)
      if (w.from === 'opinion') return opinionBody(col, w)
      if (w.from === 'sign') return ''
      return writeRow(col, w)
    })
    if (writes.some((w) => w.from === 'sign')) parts.push(signBody(col))
    return parts.join('')
  }

  const isActiveColumn = (col) => (col.writes ?? []).some((w) => w.from === activeFrom())

  function paperColumn(col) {
    const active = isActiveColumn(col)
    return `
      <section class="cc-paper-column cc-paper-${escapeHtml(col.id)}${active ? ' cc-paper-column-active' : ''}"
        data-column="${escapeHtml(col.id)}" data-active="${active}" aria-current="${active}">
        <h3 class="cc-column-label">${escapeHtml(col.label)}</h3>
        ${columnBody(col)}
      </section>`
  }

  function renderPaper() {
    const hospitalNo = recordShell.general.find((r) => r.label === '住院号')?.value ?? ''
    return `
      <div class="cc-paper">
        <header class="cc-paper-title">
          <h2 id="ccTitle">${escapeHtml(paperSpec.title)}</h2>
          <span class="cc-paper-no">${escapeHtml(hospitalNo)}</span>
        </header>
        ${paperSpec.columns.map((col) => paperColumn(col)).join('')}
      </div>`
  }

  // ── 问诊条（贴着纸的那一条） ─────────────────────────────────────────
  function answerReasonText(reasons) {
    return reasons.map((r) => {
      if (r.code === 'answer_combo_forbidden') return `这两件事凑不到一起（${r.label}）`
      if (r.code === 'answer_items_full') return `最多只能选 ${r.max} 个`
      return r.code
    }).join('；')
  }

  function questionBar(q, choice) {
    return `
      <div class="cc-ask">
        <span class="cc-doctor">${escapeHtml(interview.doctor)}</span>
        <p class="cc-ask-text">${escapeHtml(q.ask)}</p>
        <span class="cc-bar-progress">${answeredCount()} / ${interviewQuestions(db).length}</span>
      </div>
      <div class="cc-answers">
        ${choice.values.map((v) => `
          <button type="button" class="cc-answer${v.chosen ? ' active' : ''}${v.ok ? '' : ' blocked'}"
            data-answer-facet="${escapeHtml(q.facet)}" data-answer-value="${escapeHtml(v.id)}"
            aria-pressed="${v.chosen}" aria-disabled="${!v.ok}"
            ${v.ok ? '' : `title="${escapeHtml(answerReasonText(v.reasons))}"`}>${escapeHtml(v.label)}</button>`).join('')}
        ${choice.emptyOption
          ? `<button type="button" class="cc-answer${choice.emptyOption.chosen ? ' active' : ''}"
              data-answer-empty="${escapeHtml(q.facet)}"
              aria-pressed="${choice.emptyOption.chosen}">${escapeHtml(choice.emptyOption.label)}</button>`
          : ''}
      </div>
      <small class="cc-ask-note">${escapeHtml(interview.answer_note)}</small>`
  }

  function barContent() {
    if (state.stage === 'interview') {
      const q = currentQuestion()
      if (!q) return ''
      const choice = answerChoices(db, state.answers).find((c) => c.id === q.id)
      const back = state.cursor > 0
        ? `<button type="button" class="cc-bar-back" data-ask-back>${escapeHtml(interview.screen.back_question)}</button>`
        : ''
      return `${back}${questionBar(q, choice)}`
    }
    if (state.stage === 'confirm') {
      return `
        <div class="cc-ask">
          <span class="cc-doctor">${escapeHtml(interview.doctor)}</span>
          <p class="cc-ask-text">${escapeHtml(interview.screen.pool_title)}</p>
        </div>
        <small class="cc-ask-note">${escapeHtml(interview.screen.pool_note)}</small>
        <div class="cc-bar-actions">
          <button type="button" class="cc-secondary" data-ask-back>${escapeHtml(interview.screen.back_to_interview)}</button>
          <button type="button" class="cc-primary" data-pool-done ${remaining() > 0 ? 'disabled' : ''}>
            ${escapeHtml(interview.screen.pool_done)}</button>
        </div>`
    }
    if (state.stage === 'opinion') {
      const col = columnById('opinion')
      return `
        <div class="cc-ask">
          <span class="cc-doctor">${escapeHtml(interview.doctor)}</span>
          <p class="cc-ask-text">${escapeHtml(col.label)}</p>
        </div>
        <small class="cc-ask-note">${escapeHtml(interview.screen.opinion_note)} · ${escapeHtml(col.basis)}</small>
        <div class="cc-bar-actions">
          <button type="button" class="cc-secondary" data-stage="confirm">${escapeHtml(interview.screen.to_column)} · ${escapeHtml(columnWith('pool').label)}</button>
          <button type="button" class="cc-primary" data-stage="sign">${escapeHtml(interview.screen.to_column)} · ${escapeHtml(columnWith('sign').label)}</button>
        </div>`
    }
    const signCol = columnWith('sign')
    return `
      <div class="cc-ask">
        <span class="cc-doctor">${escapeHtml(interview.doctor)}</span>
        <p class="cc-ask-text">${escapeHtml(recordShell.sign.historian)}</p>
      </div>
      <small class="cc-ask-note">${escapeHtml(recordShell.sign.pending)}</small>
      <div class="cc-bar-actions">
        <button type="button" class="cc-secondary" data-stage="opinion">${escapeHtml(interview.screen.to_column)} · ${escapeHtml(columnById('opinion').label)}</button>
        <button type="button" class="cc-primary" data-confirm>${escapeHtml(recordShell.sign.consent)}</button>
      </div>
      <small class="cc-ask-note">${escapeHtml(signCol?.note ?? '')}</small>`
  }

  // ── 组装 ─────────────────────────────────────────────────────────────
  function statusText() {
    if (state.message) return state.message
    if (state.stage === 'interview') {
      const q = currentQuestion()
      return q ? `${interview.doctor} · ${q.ask}` : interview.screen.note
    }
    if (state.stage === 'confirm') {
      return remaining() > 0
        ? `还有 ${remaining()} 条没核对属实`
        : `${interview.screen.pool_title} · ${interview.screen.pool_done}`
    }
    if (state.stage === 'opinion') return interview.screen.opinion_note
    return recordShell.sign.pending
  }

  function render() {
    shell.innerHTML = `
      <header class="cc-header">
        <div><span class="cc-kicker">开局 · ${escapeHtml(recordShell.label)}</span></div>
        ${required && !state.completed
          ? '<span class="cc-required">完成人物选择后进入序章</span>'
          : '<button type="button" class="cc-close" data-close aria-label="关闭开局人物界面">×</button>'}
      </header>
      <main class="cc-body">${renderPaper()}</main>
      <footer class="cc-interview-bar">
        <div class="cc-bar-main">${barContent()}</div>
        <div class="cc-bar-foot">
          <div class="cc-status" role="status" aria-live="polite">${escapeHtml(statusText())}</div>
          <div>${import.meta.env.DEV && required && !state.completed
            ? '<button type="button" class="cc-dev-default" data-dev-default>开发默认人物 · 直接进入</button>' : ''}</div>
        </div>
      </footer>`
  }

  function open() {
    state.open = true
    root.hidden = false
    document.documentElement.classList.add('cc-open')
    render()
    ;(shell.querySelector('.cc-close') || shell.querySelector('[data-answer-value]'))?.focus()
  }

  function close() {
    if (required && !state.completed) {
      state.message = '需要完成开局人物选择后才能进入医院。'
      render()
      return false
    }
    state.open = false
    root.hidden = true
    document.documentElement.classList.remove('cc-open')
    trigger?.focus()
    return true
  }

  /** 答一问：写进纸上，然后自动进下一问。答满八问就进入既往史的核对。 */
  function answer(facet, value) {
    const q = interviewQuestions(db).find((x) => x.facet === facet)
    if (!q) {
      state.message = '没有这一问。'
      return render()
    }
    const choice = answerChoices(db, state.answers).find((c) => c.id === q.id)
    const option = choice.values.find((v) => v.id === value)
    if (option && !option.ok) {
      state.message = answerReasonText(option.reasons)
      return render()
    }
    state.answers = { ...state.answers, [facet]: value }
    // 只有参与相符判断的那几问（病前经历）会换池子；自述与时间三问只写病历，不动已核对过的条目。
    if (q.matches === true) reconcileExperiences()
    state.cursor = interviewQuestions(db).indexOf(q) + 1
    state.message = `已写下：${answerText(db, q, value)}`
    if (answeredCount() === interviewQuestions(db).length) state.stage = 'confirm'
    return render()
  }

  root.addEventListener('click', (event) => {
    if (event.target.closest('[data-close]')) return close()

    // ── 人物来源与自建姓名（页眉，不影响问诊与池子） ────────────────────
    const sourceButton = event.target.closest('[data-character-source]')
    if (sourceButton) {
      const next = sourceButton.dataset.characterSource
      if (!characterSources(db)[next]) {
        state.message = '没有这一条来源。'
        return render()
      }
      state.characterSource = next
      state.message = next === 'custom' ? '院方记录栏仍然不由你写。' : ''
      return render()
    }
    const nameButton = event.target.closest('[data-character-field]')
    if (nameButton) {
      const { characterField, value } = nameButton.dataset
      if (characterField === 'surname') state.surname = value
      else if (characterField === 'given') state.given = value
      else if (characterField === 'gender') state.gender = value
      else {
        state.message = '没有这一项。'
        return render()
      }
      const composed = state.surname && state.given
        ? composeName(db, { surname: state.surname, given: state.given })
        : null
      if (!composed && state.surname && state.given) state.message = '这两个字不在姓名候选里。'
      else state.message = composed ? `自报姓名：${composed}` : '姓与名都选一个。'
      return render()
    }

    if (event.target.closest('[data-dev-default]')) {
      state.answers = { ...developmentDefaultCharacter.answers }
      state.characterSource = defaultSourceId(db)
      state.confirmed = new Set(developmentDefaultCharacter.experiences)
      state.selectedDiseases = new Set(developmentDefaultCharacter.diseases)
      state.cursor = interviewQuestions(db).length
      state.stage = 'sign'
      state.completed = true
      state.message = '已使用开发默认人物。'
      notifyProfile()
      render()
      return close()
    }

    // ── 问诊条：答一句 ─────────────────────────────────────────────────
    const answerButton = event.target.closest('[data-answer-value]')
    if (answerButton) return answer(answerButton.dataset.answerFacet, answerButton.dataset.answerValue)
    const emptyButton = event.target.closest('[data-answer-empty]')
    if (emptyButton) return answer(emptyButton.dataset.answerEmpty, [])
    if (event.target.closest('[data-ask-back]')) {
      state.cursor = Math.max(0, state.cursor - 1)
      state.stage = 'interview'
      state.message = ''
      return render()
    }
    const reanswer = event.target.closest('[data-reanswer]')
    if (reanswer) {
      const q = questionById(db, reanswer.dataset.reanswer)
      state.cursor = interviewQuestions(db).indexOf(q)
      state.stage = 'interview'
      state.message = interview.reanswer_note
      return render()
    }

    // ── 既往史：逐条「以上属实」 ───────────────────────────────────────
    const entry = event.target.closest('[data-entry]')
    if (entry) {
      const id = entry.dataset.entry
      if (state.confirmed.has(id)) {
        state.confirmed.delete(id)
        reconcileDiseases()
        state.message = '已从既往史里去掉这一条。'
      } else {
        const verdict = canSelect(db, selectedIds(), id, poolIds())
        if (!verdict.ok) state.message = blockReasonText(verdict.reasons)
        else {
          state.confirmed.add(id)
          state.message = `以上属实：${describeExperience(db, id).title}`
        }
      }
      return render()
    }
    if (event.target.closest('[data-pool-done]')) {
      if (remaining() > 0) {
        state.message = `还有 ${remaining()} 条没核对属实。`
        return render()
      }
      state.stage = 'opinion'
      state.message = ''
      return render()
    }

    // ── 患者意见：逐条认 / 不认 ────────────────────────────────────────
    const diseaseButton = event.target.closest('[data-disease]')
    if (diseaseButton) {
      const id = diseaseButton.dataset.disease
      if (state.selectedDiseases.has(id)) state.selectedDiseases.delete(id)
      else {
        const verdict = diseaseCanStillPick(db, ddb, selectedIds(), id)
        if (!verdict.ok) {
          state.message = verdict.reasons
            .map((r) => (r.code === 'not_in_candidates' ? '这一条不在候选里' : `最多只能认 ${r.max} 种`))
            .join('；')
          return render()
        }
        state.selectedDiseases.add(id)
      }
      state.message = state.selectedDiseases.has(id) ? `已认下：${diseaseLabel(id)}` : '已划掉。'
      return render()
    }

    const stageButton = event.target.closest('[data-stage]')
    if (stageButton) {
      state.stage = stageButton.dataset.stage
      state.message = ''
      return render()
    }

    // ── 落款 ───────────────────────────────────────────────────────────
    if (event.target.closest('[data-confirm]')) {
      if (remaining() > 0) {
        state.message = `还有 ${remaining()} 条没核对属实。`
        state.stage = 'confirm'
        return render()
      }
      state.completed = true
      state.message = '开局人物已确认。'
      notifyProfile()
      render()
      return close()
    }
    return undefined
  })

  root.addEventListener('click', (event) => {
    if (event.target === root) close()
  })

  document.addEventListener('keydown', (event) => {
    if (!state.open) return
    if (event.key === 'Escape') {
      event.preventDefault()
      close()
    }
    // 模态界面打开时，不让数字键或移动键继续驱动背后的叙事/三维场景。
    event.stopImmediatePropagation()
  }, true)
  trigger?.addEventListener('click', open)

  return {
    open,
    close,
    getProfile: profile,
    get completed() { return state.completed },
    subscribe(listener) {
      profileListeners.add(listener)
      return () => profileListeners.delete(listener)
    },
  }
}
