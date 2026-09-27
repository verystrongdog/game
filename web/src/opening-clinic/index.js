/**
 * 开局门诊病历 · **界面层**：这一屏就是游戏里的那一屏——**左边世界 · 右边叙事流**。
 *
 * 来源：design/presentation/叙事界面布局.md §二「屏幕结构」（左侧世界承担空间与可交互物提示，
 * 右侧是叙事流：说话者 / 客观描述 / 玩家回应）与 design/presentation/开局门诊问诊.md §十一。
 *
 * owner 2026-09-27 阶段 6 的三条裁定（这一版就是按它们重做的）：
 *   ① 现在的对话模式像填表——问诊要在**游戏里的界面**里进行（不是把现实里的病历表照搬上屏）；
 *   ② **病史陈述要整合成句**，不许把对话里的词一行一行照抄到纸上；
 *   ③ 玩家**通过对话选择塑造自己的人格**——患者怎么说话，就是他的病在哪儿现形（语言指纹）。
 *
 * 所以这一屏现在是：
 *   - 左侧「诊室」：桌上摊着那份门诊初诊病历（**一直看得见**），随问诊一句一句写满；病史栏是整段句子；
 *   - 右侧「叙事面板」：医师问一句 · 患者答一句（带着他的说话调子）· 医师落笔一句，**回应接着排在流的末尾**，
 *     可以点，也可以按数字键。整栏**只有一个滚动条**。
 *
 * 🔧 **阶段 7 之后的三条形态裁定（owner 2026-09-27 在真浏览器里看过成品之后）**：
 *   ① **纸不随每次点击滚到底**：换 innerHTML 会丢掉那张纸的滚动位置，所以渲完把它放回去；
 *      只有「正在填的那一栏」**换了**才 `scrollIntoView({ block: 'nearest' })` 一次，**不做平滑动画**；
 *      右栏叙事流**不**再「永远滚到最底」——改成**让回应整块进视野**（见下面第四条）。
 *   ② **右栏不再分成上下两段**：回应从「钉在底部的第二个滚动区」改成**叙事流末尾的一块**（`.oc-now`），
 *      整栏只有一个滚动容器；`data-responses` / `data-choice-index` / `data-candidates` / `data-disease` 语义不变。
 *   ③ **调子的颜色只画在选项上**（左边一条细边 + 调子名那一小块），是**冗余**信息：调子名一直写着。
 *      ⚠️ 它是**言语指纹的分组色**，不是被否决的「颜色表示情绪/态度」那套体系
 *      （design/conventions/README.md §二 第 46 行禁的是后者）。
 *   ④ **叙事流的滚动 = 让回应整块进视野**（追加裁定）：块 + 24px 装得下 → 滚到刚好带进视野的
 *      最小位置；块比视野还高 → 从块顶往上留 24px 起读；拿不到尺寸才回落到「滚到最底」。
 *
 * 全部栏目名、问法、答案取值、落笔模板与上屏文案都从 `data/opening_clinic.json` 读。
 * **本文件里没有任何自由文本入口**：玩家只有三种笔——**答 · 认不了（那一档「不愿说」）· 签**。
 *
 * 🔧 **阶段 7（2026-09-27）：经历与疾病接回这一屏。** owner 裁定「经历首先需要满足能够激活疾病」、
 * 「疾病诱因往往是围绕着一件事展开的」、「设计要为游戏服务」——所以一局的经历不再是十段散点，
 * 而是**一件事**：问诊答案定位出它 → 它激活的病（候选 ≤4）→ 玩家在对话里**认**下一张 →
 * 医师把「初步诊断」写上纸 → 那张病反过来驱动他怎么说话（语言指纹）与精神检查那三行。
 * 界面这一轮只做五件事（口径文档 `design/presentation/开局经历疾病接回.md` §十 的接线契约）：
 *   ① 那件事进叙事流（文案全在 `data/opening_clinic.json` 的 `event_wiring.ui`）；
 *   ② 候选以回应形式摆在流的末尾（数字键 1–9），认下即落笔——**不新开一屏**；
 *   ③ `state.disease` 一旦有值，纸上诊断栏与精神检查三行由 `paperColumns` 现算。⚠️ 渲染器**有一处**
 *      必须动：`derived` 栏在还没落笔时要看得见它的**空白态**（不然诊断栏认病之前整栏一个字都没有）；
 *   ④ 「他说话的样子」那一行认了病之后按**病**取（`voice_of_disease`）；
 *   ⑤ 认下之后「改一改」把那张病对回候选：不在候选里就退回没认（诊断栏随之回到空白态）。
 *
 * 边界（AGENTS.md §二 拦截规则）：只服务开局 / Web 演示，不得引入 C# 引擎或神经模拟系统的任何概念；
 * 战斗相关内容一律不碰。经历池（八问 → 池子 → 认满十段）自阶段 7 起**退役**，键与代码原样留着。
 */

import clinic from '../../../data/opening_clinic.json'
import diseases from '../../../data/diseases.json'
import opening from '../../../data/opening.json'
import {
  characterOptions,
  composeName,
  defaultSourceId,
  hospitalIdentity,
  optionLabel,
} from '../character-creation/character-source.js'
import {
  activeColumnId,
  answerLimitOf,
  applyAnswer,
  canSign,
  candidateBasis,
  chiefComplaint,
  confirmDisease,
  confirmedDiseaseId,
  currentQuestion,
  dialogueTurns,
  eventDiseaseCandidates,
  eventOf,
  isMulti,
  isRefuse,
  optionsOf,
  paperColumns,
  probesOf,
  profileOf,
  progressOf,
  reAnswer,
  voiceOfDisease,
  voiceTally,
} from './opening-clinic.js'

const escapeHtml = (value) => String(value)
  .replaceAll('&', '&amp;')
  .replaceAll('<', '&lt;')
  .replaceAll('>', '&gt;')
  .replaceAll('"', '&quot;')

const ui = clinic.ui

// 阶段 7 的上屏文案（那件事 / 候选 / 认下诊断 / 言语随病）。`{...}` 是占位符，由这里替换。
// ⚠️ 界面代码里**不写中文文案字面量**（提示词 §一 第 5 条）——这一屏要说的话全在数据里。
const wiring = clinic.event_wiring?.ui ?? {}
const copy = (template, vars = {}) => String(template ?? '').replace(/\{(\w+)\}/g, (_, key) => vars[key] ?? '')

export function createOpeningClinic({ trigger = null, required = false } = {}) {
  const listeners = new Set()
  const state = {
    open: false,
    answers: {},
    signed: false,
    disease: null,
    message: '',
    characterSource: defaultSourceId(opening),
    surname: null,
    given: null,
    gender: null,
    seenContentNotes: new Set(),
  }

  // 那张纸的滚动位置与「上一次正在填的是哪一栏」——裁定 ①：位置要留住，只有换栏才滚一次。
  let paperScrollTop = 0
  let lastPaperColumn = null
  // 叙事流滚动时给回应块上方留的空白（owner 2026-09-27 追加裁定里写死的 24px）。
  const STORY_GAP = 24

  const root = document.createElement('div')
  root.className = 'oc-overlay'
  root.hidden = true
  root.innerHTML = '<main class="oc-shell" role="dialog" aria-modal="true" aria-labelledby="ocTitle" data-shell="1"></main>'
  document.body.append(root)
  const shell = root.querySelector('.oc-shell')

  const options = characterOptions(opening)
  const identity = hospitalIdentity(opening)

  // ── 派生状态（一律现算） ────────────────────────────────────────────────
  function character() {
    const composed = state.surname && state.given ? composeName(opening, { surname: state.surname, given: state.given }) : null
    const base = {
      source: state.characterSource,
      ...(composed ? { name: composed } : {}),
      ...(state.gender ? { gender: state.gender } : {}),
    }
    return {
      ...base,
      genderLabel: optionLabel(opening, 'gender', state.gender),
      hospitalName: identity?.hospital_name ?? null,
    }
  }

  const isCustom = () => state.characterSource === 'custom'
  const current = () => currentQuestion(clinic, state)
  const complete = () => current() === null
  const tally = () => voiceTally(clinic, state)

  // 阶段 7 的三样现算：一局的那件事（恰一件）· 它激活的病（候选 ≤4）· 本局**认**下的那一张。
  const eventNow = () => eventOf(clinic, opening, state)
  const candidateState = () => eventDiseaseCandidates(clinic, opening, diseases, state)
  const confirmedId = () => confirmedDiseaseId(state)
  const diseaseLabelOf = (id) => diseases.items.find((d) => d.id === id)?.label ?? id

  function notify() {
    const value = profileOf(clinic, state, { character: character() })
    listeners.forEach((listener) => listener(value))
  }

  // ── 左边：诊室，桌上是那份一直看得见的病历 ──────────────────────────────

  const inkTag = (ink) => (ink ? `<span class="oc-ink oc-ink-${ink}">${escapeHtml(clinic.record.ink[ink].label)}</span>` : '')

  /** 纸上的一栏。整段病史用 `column.text`（拼出来的句子）；能改的地方给「改一改」的小按钮。 */
  function paperColumn(column_, activeId) {
    const ink = column_.ink ?? (column_.who === 'patient' ? 'patient' : 'hospital')
    const derivedLine = column_.fill === 'derived' && column_.resolved
      ? `<p class="oc-write oc-write-source oc-ink-hospital"><span class="oc-write-text">${escapeHtml(column_.text)}</span></p>`
      : ''

    let body
    if (column_.fill === 'derived') {
      // 主诉：上面一行是院方按法定格式写成的成品，下面是患者说的那两句（可改）；
      // 诊断栏（阶段 7）：认下之前**必须看得见它的空白态**——那一栏不是不存在，是医师还没落笔
      // （`paperColumns` 已经把 `column_.text` 给成 `blank`，这里不能把它丢掉）。
      body = column_.resolved
        ? derivedLine
        : `<p class="oc-write oc-blank oc-ink-${ink}"><span class="oc-write-text">${escapeHtml(column_.blank)}</span></p>`
    } else if (column_.composed) {
      // 整段病史：一句一句连着写，不是一问一行
      body = `<p class="oc-write oc-write-prose oc-ink-${ink}"><span class="oc-write-text">${escapeHtml(column_.text || column_.blank)}</span></p>`
    } else if (column_.rows?.length) {
      body = column_.rows.map((row) => `<p class="oc-write oc-ink-${row.ink}"${row.questionId ? ` data-write-from="${row.questionId}"` : ''}>
        ${row.lead ? `<span class="oc-write-label">${escapeHtml(row.lead)}</span>` : ''}
        <span class="oc-write-text">${escapeHtml(row.text)}</span>
      </p>`).join('')
    } else {
      body = `<p class="oc-write ${column_.resolved ? '' : 'oc-blank'} oc-ink-${ink}">
        <span class="oc-write-text">${escapeHtml(column_.text || column_.blank)}</span>
      </p>`
    }

    const unresolved = (column_.unanswered ?? []).length
      ? `<p class="oc-write-void"><span>${escapeHtml(ui.unanswered_label)}</span>${column_.unanswered.map((u) => `<i>${escapeHtml(u.lead)}</i>`).join('')}</p>`
      : ''

    const reanswerable = column_.who === 'patient' && column_.fill !== 'hospital' && (column_.rows ?? []).length
      ? `<p class="oc-reanswers">${column_.rows.filter((r) => r.questionId).map((r) => `<button class="oc-reanswer" data-reanswer="${r.questionId}" data-write-from="${r.questionId}" title="${escapeHtml(r.ask)}">${escapeHtml(r.lead || r.ask)}</button>`).join('')}</p>`
      : ''

    return `<section class="oc-paper-column${column_.id === activeId ? ' oc-paper-column-active' : ''}" data-column="${column_.id}" data-who="${column_.who}">
      <p class="oc-column-label">${escapeHtml(column_.label)}${column_.id === activeId ? ` · ${escapeHtml(ui.column_open_tag)}` : ''}</p>
      ${inkTag(column_.who === 'patient' ? 'patient' : 'hospital')}
      ${body}
      ${unresolved}
      ${reanswerable}
      ${column_.screen_note ? `<p class="oc-column-note">${escapeHtml(column_.screen_note)}</p>` : ''}
    </section>`
  }

  function paper() {
    const activeId = activeColumnId(clinic, state)
    const columns = paperColumns(clinic, state, { character: character(), signed: state.signed, legacyCharacterSource: { identity } })
    const homepage = columns.filter((c) => c.group === 'homepage')
    const body = columns.filter((c) => c.group === 'body')
    const notOpen = clinic.record.not_open

    return `<article class="oc-paper" data-pane="paper">
      <div class="oc-paper-title">
        <h2 id="ocTitle">${escapeHtml(clinic.record.title)}</h2>
        <span class="oc-paper-no">${escapeHtml(ui.ink_legend)}</span>
      </div>
      <div class="oc-paper-scroll">
        <section class="oc-homepage" data-group="homepage">
          <p class="oc-group-label">${escapeHtml(ui.homepage_label)}</p>
          <div class="oc-record-head">${homepage.map((c) => paperColumn({ ...c, rows: [] }, activeId)).join('')}</div>
          ${characterPicker()}
        </section>
        <section class="oc-record-body" data-group="body">
          ${body.map((c) => paperColumn(c, activeId)).join('')}
        </section>
        <p class="oc-column-note oc-paper-foot">${escapeHtml(clinic.record.paper_note)}</p>
        <p class="oc-column-note oc-paper-foot">${notOpen.map((n) => `${n.label}：${n.why}`).map(escapeHtml).join('　')}</p>
      </div>
    </article>`
  }

  function characterPicker() {
    const sourceButtons = Object.entries(opening.character_source.characters)
      .map(([id, spec]) => `<button class="oc-character-option${id === state.characterSource ? ' active' : ''}" data-character-source="${id}">${escapeHtml(spec.label)}</button>`)
      .join('')
    const genderButtons = options.gender.values
      .map((v) => `<button class="oc-character-option${v.id === state.gender ? ' active' : ''}" data-character-field="gender" data-character-value="${v.id}">${escapeHtml(v.label)}</button>`)
      .join('')
    const chips = (group, currentValue, field) => `<span class="oc-name-group"><i>${escapeHtml(group.label)}</i>${group.values.map((v) => `<button class="oc-name-chip${currentValue === v ? ' active' : ''}" data-character-field="${field}" data-character-value="${escapeHtml(v)}">${escapeHtml(v)}</button>`).join('')}</span>`
    return `<div class="oc-character">
      <span class="oc-character-label">${escapeHtml(ui.character_label)}</span>
      ${sourceButtons}
      ${isCustom ? `<div class="oc-name-picker">${chips(options.name.surname, state.surname, 'surname')}${chips(options.name.given, state.given, 'given')}</div>
        <div class="oc-name-picker"><span class="oc-name-group"><i>${escapeHtml(options.gender.label)}</i>${genderButtons}</span></div>` : ''}
      <span class="oc-character-note">${escapeHtml(ui.character_note)}</span>
    </div>`
  }

  /** 左侧世界：诊室（地点 / 时段 / 状态条 · 桌面上的那张纸）。 */
  function world() {
    const progress = progressOf(clinic, state)
    return `<section class="oc-world" data-pane="world" aria-label="${escapeHtml(ui.place)}">
      <header class="oc-world-top">
        <span class="oc-place">${escapeHtml(ui.place)}</span>
        <span class="oc-when">${escapeHtml(ui.when)}</span>
        <span class="oc-world-progress">${escapeHtml(ui.progress.replace('{index}', progress.index).replace('{total}', progress.total))}</span>
        <button class="oc-close" data-close="1" aria-label="${escapeHtml(ui.close)}">×</button>
      </header>
      <div class="oc-desk">
        <span class="oc-lamp" aria-hidden="true"></span>
        ${paper()}
      </div>
      <footer class="oc-world-foot">
        <span>${escapeHtml(ui.world_note)}</span>
        <span class="oc-status" data-status="1">${escapeHtml(state.message || ui.status_answering)}</span>
      </footer>
    </section>`
  }

  // ── 右边：叙事面板（说话者条 · 调子条 · **一个**滚动区：叙事流 + 末尾那一块回应） ────

  /** 一条叙事：医师问 / 患者答 / 落笔。都按「标签 + 正文」摊在同一个流里（叙事界面布局 §三）。 */
  function beat(turn) {
    if (turn.kind === 'system') {
      return `<article class="oc-beat oc-beat-system" data-turn="system">
        <span class="oc-beat-label">${escapeHtml(ui.content_note_label)} · ${escapeHtml(turn.label)}</span>
        <p class="oc-beat-text">${escapeHtml(turn.text)}</p>
      </article>`
    }
    if (turn.kind === 'patient') {
      const voice = turn.voiceLabel ? `<span class="oc-beat-voice">${escapeHtml(turn.voiceLabel)}</span>` : ''
      const refusal = turn.refuse ? `<span class="oc-beat-refuse">${escapeHtml(ui.refuse_tag)}</span>` : ''
      return `<article class="oc-beat oc-beat-patient oc-ink-patient" data-turn="patient" data-turn-q="${escapeHtml(turn.id)}">
        <span class="oc-beat-label">${escapeHtml(ui.patient_tag)}${voice}${refusal}</span>
        <p class="oc-beat-text">${escapeHtml(turn.text)}</p>
      </article>`
    }
    if (turn.kind === 'note') {
      return `<article class="oc-beat oc-beat-note" data-turn="note" data-turn-q="${escapeHtml(turn.id)}">
        <span class="oc-beat-label">${escapeHtml(ui.note_tag)}</span>
        <p class="oc-beat-text">${escapeHtml(turn.text)}</p>
      </article>`
    }
    const chips = [
      turn.required ? ui.required_tag : '',
      turn.followup ? ui.followup_tag : '',
      turn.moduleLabel ?? '',
    ].filter(Boolean).map((t) => `<span class="oc-beat-chip">${escapeHtml(t)}</span>`).join('')
    const why = turn.followup && turn.triggerLabel ? `<span class="oc-beat-why">${escapeHtml(turn.triggerLabel)}</span>` : ''
    return `<article class="oc-beat oc-beat-doctor" data-turn="doctor" data-turn-q="${escapeHtml(turn.id)}">
      <span class="oc-beat-label">${escapeHtml(ui.doctor_tag)}${chips}${why}</span>
      <p class="oc-beat-text">${escapeHtml(turn.text)}</p>
    </article>`
  }

  /**
   * 那件事进叙事流（提示词 §九 第 2 条 · 口径文档 §10.2 第 2 条）。
   *
   * 时机：问诊问完（`complete()`）之后——也就是候选摆出来的那一拍。它**不是**第二份状态：
   * 那件事由 `eventOf()` 从 `state.answers` 现算，玩家「改一改」时它跟着换。
   * 三条文案全部来自 `data/opening_clinic.json` 的 `event_wiring.ui`；本文件不新增中文文案。
   */
  function eventTurns() {
    if (!complete()) return []
    const event = eventNow()
    if (!event) return []
    const turns = [
      { kind: 'doctor', id: 'event', text: copy(wiring.event_ask, { title: event.title }), required: false, followup: false },
      { kind: 'note', id: 'event', text: copy(wiring.event_note) },
    ]
    const id = confirmedId()
    // 认下之后补一条落笔：写的是**医师把哪一张写进了诊断栏**（纸上的那一栏由 paperColumns 现算）。
    if (id) turns.push({ kind: 'note', id: 'event-confirmed', text: copy(wiring.confirmed_note, { label: diseaseLabelOf(id) }) })
    return turns
  }

  /**
   * 右栏**只有一个滚动容器**：叙事流 + 它的末尾那一块「现在该你说了」（owner 2026-09-27 形态裁定 ②）。
   *
   * 回应不是第二个滚动区、也不再「钉在底部」——它就是叙事流的**末尾一块**：医师问完最后一句，
   * 底下的选项接着往下排，整栏一个滚动条。玩家选完，那一块由「患者说」那条 beat 接替（`dialogueTurns`
   * 里那条已经是这个作用），不会留下两份。`data-responses` / `data-choice-index` / `data-candidates` /
   * `data-disease` 的语义一个字没变（测试与 `render-clinic.mjs --check` 都靠它们）。
   */
  function story() {
    const turns = [...dialogueTurns(clinic, state), ...eventTurns()]
    return `<div class="oc-story" data-log="1">${turns.map(beat).join('')}${now()}</div>`
  }

  /** 叙事流末尾那一块：当前那一问 + 玩家挑的那一句（点或按数字键）。 */
  function now() {
    const question = current()
    if (question) {
      const multi = isMulti(clinic, question)
      const limit = answerLimitOf(clinic, question)
      const chosen = state.answers[question.id]
      const level = question.sensitive ? clinic.sensitivity_levels[question.sensitive] : null
      const probes = probesOf(clinic, question)
      const chips = [
        question.required ? ui.required_tag : '',
        question.followup ? ui.followup_tag : '',
        question.module ? (clinic.module_labels?.[question.module] ?? '') : '',
      ].filter(Boolean).map((t) => `<span class="oc-beat-chip">${escapeHtml(t)}</span>`).join('')
      const why = question.followup && question.trigger?.label ? `<span class="oc-beat-why">${escapeHtml(question.trigger.label)}</span>` : ''
      return `<section class="oc-now" data-now="1" data-responses="1">
        ${level ? `<p class="oc-content-note"><b>${escapeHtml(ui.content_note_label)} · ${escapeHtml(level.label)}</b>${escapeHtml(level.content_note)}</p>` : ''}
        <article class="oc-beat oc-beat-doctor oc-beat-current" data-turn="doctor" data-turn-q="${escapeHtml(question.id)}">
          <span class="oc-beat-label">${escapeHtml(ui.doctor_tag)}${chips}${why}</span>
          <p class="oc-beat-text">${escapeHtml(question.ask)}</p>
        </article>
        ${probes.length ? `<p class="oc-probes"><span class="oc-probes-label">${escapeHtml(ui.probes_label)}</span>${probes.map((p) => `<span class="oc-probe">${escapeHtml(p.ask)}</span>`).join('')}</p>` : ''}
        <p class="oc-responses-label">${escapeHtml(ui.responses_label)}<span>${escapeHtml(ui.response_hint)}</span></p>
        ${choices(question, multi, limit, chosen)}
      </section>`
    }
    if (!state.signed) {
      return `<section class="oc-now" data-now="1" data-responses="1">
        <article class="oc-beat oc-beat-doctor oc-beat-current"><span class="oc-beat-label">${escapeHtml(ui.doctor_tag)}</span><p class="oc-beat-text">${escapeHtml(ui.no_more)}</p></article>
        ${diagnosis()}
        <p class="oc-content-note">${escapeHtml(ui.sign_note)}</p>
        <div class="oc-choices"><button class="oc-choice oc-choice-primary" data-sign="1"${canSign(clinic, state) ? '' : ' disabled'}>${escapeHtml(ui.sign_action)}</button></div>
      </section>`
    }
    return `<section class="oc-now" data-now="1" data-responses="1">
      <article class="oc-beat oc-beat-doctor oc-beat-current"><span class="oc-beat-label">${escapeHtml(ui.doctor_tag)}</span><p class="oc-beat-text">${escapeHtml(ui.signed_note)}</p></article>
      <div class="oc-choices"><button class="oc-choice oc-choice-primary" data-confirm="1">${escapeHtml(ui.launch)}</button></div>
    </section>`
  }

  /** 玩家的回应：闭集 + 那一档「不愿说」；打了语言指纹的档，按钮上标出他这一句是什么调子。 */
  function choices(question, multi, limit, chosen) {
    const buttons = optionsOf(clinic, question).map((option, index) => {
      const on = multi ? Array.isArray(chosen) && chosen.includes(option.id) : chosen === option.id
      const profile = option.voice ? clinic.voices.items.find((v) => v.id === option.voice) : null
      const voice = profile ? `<span class="oc-choice-voice">${escapeHtml(profile.screen_name)}</span>` : ''
      // 调子的颜色：只画在**选项**上（左边一条细边 + 调子名那一小块）。颜色是**冗余**信息，
      // 「沉下去 / 往上冲 …」这几个字一直写着（owner 2026-09-27 形态裁定 ③）。
      const voiceTone = profile ? ` oc-voice-${profile.id}` : ''
      return `<button class="oc-choice${on ? ' on' : ''}${isRefuse(clinic, option.id) ? ' oc-choice-refuse' : ''}${voiceTone}"
        data-answer-value="${escapeHtml(option.id)}" data-choice-index="${index + 1}">
        <b class="oc-choice-no">${index + 1}</b>${voice}<span class="oc-choice-text">${escapeHtml(option.label)}</span>
      </button>`
    }).join('')
    return `<div class="oc-choices">${buttons}</div>
      <div class="oc-choices-foot">
        <button class="oc-choice-back" data-ask-back="1">${escapeHtml(ui.back)}</button>
        ${multi ? `<button class="oc-choice oc-choice-primary" data-answer-commit="1"${Array.isArray(chosen) && chosen.length >= limit.min ? '' : ' disabled'}>${escapeHtml(ui.continue)}</button>
          <span class="oc-status">${escapeHtml(ui.multi_hint.replace('{min}', limit.min).replace('{max}', limit.max))}</span>` : ''}
      </div>`
  }

  /**
   * 认下诊断：候选（≤4）以**回应**形式摆在叙事流的末尾，认下即由医师落笔（口径文档 §10.2 第 3 条）。
   *
   * 候选 = 那件事激活的病，减去已答扩展位声明排除的；一局说话的调子显出来之后，收窄到该调子
   * 代言的那一张——「**怎么说话就是在说哪张病**」（owner 第 7 条）。调子还没显出来（打标档不足
   * `voices.min_tagged`）时 4 张全摆出来由玩家挑。
   *
   * **不新开一屏、纸上不加「患者意见」栏**（门诊初诊的法定栏目里没有这一栏，自造栏目违反「不许自造」）：
   * 玩家只做「认」这一个动作，笔落在医师手里——`state.disease` 一有值，纸上诊断栏与精神检查三行
   * 由 `paperColumns` 现算，渲染器一个字都不用改。
   */
  function diagnosis() {
    const { candidates, narrowed } = candidateState()
    if (!candidates.length) return ''
    const only = narrowed.length === 1 ? candidates[0] : null
    const head = `<article class="oc-beat oc-beat-doctor" data-turn="doctor" data-turn-q="candidate">
      <span class="oc-beat-label">${escapeHtml(ui.doctor_tag)}</span>
      <p class="oc-beat-text">${escapeHtml(only ? copy(wiring.candidate_narrowed, { label: only.label }) : copy(wiring.candidate_prompt))}</p>
    </article>`
    const rows = candidates.map((candidate, index) => {
      const on = confirmedId() === candidate.id
      const basis = candidateBasis(clinic, opening, diseases, state, candidate.id)
      // 「因为你有那件事：…」——候选为什么在这儿。`candidate_basis` 是数据里的模板；
      // 取不到模板时回落到 `candidate_basis_fallback`（本批数据两份都在，退路不触发）。
      const because = basis?.screen ?? (basis ? copy(wiring.candidate_basis_fallback, { title: basis.title }) : null)
      return `<li class="oc-candidate${on ? ' on' : ''}" data-candidate="${escapeHtml(candidate.id)}"${on ? ' data-confirmed="1"' : ''}>
        <span class="oc-candidate-label">${escapeHtml(candidate.label)}</span>
        ${candidate.plain ? `<span class="oc-candidate-plain">${escapeHtml(candidate.plain)}</span>` : ''}
        ${because ? `<span class="oc-candidate-basis">${escapeHtml(because)}</span>` : ''}
        <button class="oc-choice oc-choice-primary" data-disease="${escapeHtml(candidate.id)}" data-choice-index="${index + 1}">${escapeHtml(copy(wiring.confirm_action))}</button>
      </li>`
    }).join('')
    return `${head}<div class="oc-candidates" data-candidates="1">
      <p class="oc-responses-label">${escapeHtml(ui.responses_label)}<span>${escapeHtml(ui.response_hint)}</span></p>
      <ul class="oc-candidate-list">${rows}</ul>
    </div>${only ? '' : `<p class="oc-content-note">${escapeHtml(copy(wiring.candidate_none))}</p>`}`
  }

  /** 说话的调子：一局里累积出来的那一套（不足三档就说还听不出来）；认了病之后按**病**取。 */
  function voiceLine() {
    const value = tally()
    const id = confirmedId()
    const spoken = id ? voiceOfDisease(clinic, id) : null
    // 认了病之后这一行**按病取**（口径文档 §10.2 第 4 条）：读作「这张病在他嘴里是什么样」，
    // 不再读作「这一局的调子」——owner 第 7 条：怎么说话就是在说哪张病。
    const known = spoken
      ? `<b>${escapeHtml(copy(wiring.voice_of_disease, { voice: spoken.screen_name }))}</b>`
      : value.dominant
        ? `<b>${escapeHtml(ui.voice_legend)}：${escapeHtml(value.dominantLabel)}</b>`
        : `<b>${escapeHtml(ui.voice_legend)}：${escapeHtml(copy(wiring.voice_unknown_still) || ui.voice_unknown)}</b>`
    // 只列已经出现过的调子：一局刚开始时不该摆四个 0 在那儿。
    const counts = clinic.voices.items
      .filter((v) => (value.counts[v.id] ?? 0) > 0)
      .map((v) => `<i${v.id === value.dominant ? ' class="on"' : ''}>${escapeHtml(v.screen_name)} ${value.counts[v.id]}</i>`)
      .join('')
    return `<p class="oc-voice-line"${spoken ? ` data-voice-disease="${escapeHtml(id)}"` : ''}>${known}${counts ? `<span class="oc-voice-counts">${counts}</span>` : ''}</p>`
  }

  function panel() {
    const question = current()
    const charter = character()
    const speaker = state.signed ? ui.speaker_signed : (question ? ui.speaker_doctor : ui.speaker_doctor_done)
    return `<aside class="oc-panel" data-pane="dialogue" aria-label="${escapeHtml(ui.bar_title)}">
      <header class="oc-panel-header">
        <div class="oc-speaker-mark" aria-hidden="true">${escapeHtml(ui.doctor_mark)}</div>
        <div class="oc-speaker-heading">
          <p class="oc-eyebrow">${escapeHtml(ui.kicker)}</p>
          <h1>${escapeHtml(speaker)}</h1>
          <p>${escapeHtml(charter.name ? ui.speaker_patient_note.replace('{name}', charter.name) : ui.speaker_patient_unknown)}</p>
        </div>
        <span class="oc-tab">${escapeHtml(ui.bar_title)}</span>
      </header>
      ${voiceLine()}
      ${story()}
    </aside>`
  }

  /**
   * 把「正在填的那一栏」滚进视野——**只在换栏的那一次做**，且不做平滑动画
   * （owner 2026-09-27 形态裁定 ①：纸不随每次点击滚到底；同一栏里连续落笔不滚）。
   *
   * 主路按**视口矩形**算（`getBoundingClientRect`）——它就是 `block: 'nearest'` 的语义，
   * 而且**不依赖 `offsetParent`**（`offsetTop` 在真浏览器里未必相对滚动容器，中间隔一个
   * `position: relative` 就偏了）。这条路**无头桩里也走得到**，所以生产路径就是被测过的那一条。
   * 拿不到矩形的宿主才回落到 `scrollIntoView({ block: 'nearest' })`。
   */
  function scrollPaperToActiveColumn() {
    const paperEl = shell.querySelector ? shell.querySelector('.oc-paper-scroll') : null
    const active = shell.querySelector ? shell.querySelector('.oc-paper-column-active') : null
    if (!paperEl || !active) return
    const seen = Number(paperEl.scrollTop ?? 0)
    const rect = typeof active.getBoundingClientRect === 'function' ? active.getBoundingClientRect() : null
    const view = typeof paperEl.getBoundingClientRect === 'function' ? paperEl.getBoundingClientRect() : null
    if (rect && view) {
      // 上沿在视野之上 → 对齐上沿；下沿在视野之下 → 对齐下沿；本来就看得见 → 什么都不做。
      if (rect.top < view.top) paperEl.scrollTop = seen - (view.top - rect.top)
      else if (rect.bottom > view.bottom) paperEl.scrollTop = seen + (rect.bottom - view.bottom)
      paperScrollTop = Number(paperEl.scrollTop ?? 0)
      return
    }
    if (typeof active.scrollIntoView === 'function') {
      active.scrollIntoView({ block: 'nearest' })
      if (typeof paperEl.scrollTop === 'number') paperScrollTop = paperEl.scrollTop
    }
  }

  /**
   * 叙事流的滚动：**让回应整块进视野**，不再「永远滚到最底」（owner 2026-09-27 追加裁定）。
   *
   * 三档，判据是机核的：
   *   ① 回应块（`.oc-now`）高度 + 上方 24px 留白 **≤ 可视高度** → 滚到「刚好把整块连同那 24px
   *      带进视野的**最小**位置」= `min(最大滚动量, 块底 + 24 − clientHeight)`（下限 0）——
   *      这样前面医师那一句能留多少留多少；
   *   ② 块**比可视高度还高** → 滚到 `min(最大滚动量, 块顶 − 24)`（下限 0），
   *      让玩家从提示那一行往下读，而不是只看见选项的下半截；
   *   ③ 拿不到 `clientHeight` / `offsetTop` → 回落到原来的「滚到最底」。
   *
   * ⚠️ `offsetTop` 相对的是**定位祖先**：`.oc-story` 在 CSS 里给了 `position: relative`，
   * 所以这里量到的就是「在流里的位置」。这一条路**无头桩里也走得到**（两条分支都有判据）。
   */
  function scrollStoryToNow() {
    const storyEl = shell.querySelector ? shell.querySelector('.oc-story') : null
    if (!storyEl) return
    const nowEl = shell.querySelector ? shell.querySelector('.oc-now') : null
    const view = Number(storyEl.clientHeight ?? NaN)
    const top = Number(nowEl?.offsetTop ?? NaN)
    const height = Number(nowEl?.offsetHeight ?? NaN)
    if (!nowEl || !Number.isFinite(view) || view <= 0 || !Number.isFinite(top) || !Number.isFinite(height)) {
      storyEl.scrollTop = storyEl.scrollHeight              // ③ 拿不到就拿不到：滚到最底
      return
    }
    const max = Math.max(0, Number(storyEl.scrollHeight ?? 0) - view)
    const wanted = height + STORY_GAP <= view
      ? top + height + STORY_GAP - view                      // ① 整块 + 24px 刚进视野
      : top - STORY_GAP                                      // ② 比视野还高：从块顶往上留 24px 起读
    storyEl.scrollTop = Math.max(0, Math.min(max, wanted))
  }

  function render() {
    // 换 innerHTML 会把那张纸的滚动位置一起丢掉，所以先记住、渲完放回去（裁定 ①：
    // 「不许每次点击都滚到底」= 位置要留住，而不是每次跳回纸头）。
    const before = shell.querySelector ? shell.querySelector('.oc-paper-scroll') : null
    if (before && typeof before.scrollTop === 'number') paperScrollTop = before.scrollTop
    shell.innerHTML = `${world()}${panel()}`
    // 叙事流：让回应整块进视野（追加裁定，取代原来的「滚到最底」）。
    scrollStoryToNow()
    const paperEl = shell.querySelector ? shell.querySelector('.oc-paper-scroll') : null
    if (paperEl && typeof paperScrollTop === 'number') paperEl.scrollTop = paperScrollTop
    // 只有「正在填的那一栏」换了，才把它滚进视野；同一栏里连续落笔原地不动。
    const activeId = activeColumnId(clinic, state)
    if (activeId !== lastPaperColumn) {
      lastPaperColumn = activeId
      scrollPaperToActiveColumn()
    }
  }

  // ── 交互 ───────────────────────────────────────────────────────────────

  function setMessage(text) { state.message = text }

  /** 答完之后世界下沿那句状态：问完了就换成「可以落款」那一句（`status_ready_sign`，阶段 5 的文案）。 */
  function afterAnswer(dropped = []) {
    setMessage(dropped.length ? ui.status_reanswering : (complete() ? ui.status_ready_sign : ui.status_answering))
    reconcileDisease()
  }

  /**
   * 改答案之后把**认下的那一张**对回候选。
   *
   * 「落款之前，纸上写的每一句都还能回去改」（`ui.status_ready_sign`）——所以这一局随时可能回头改答案：
   * 一改，那件事可能换成另一件、他说话的调子可能倒向另一套，**候选也就换了**。这时如果还留着原来认下的
   * 那一张，它就成了一张 `confirmDisease()` 自己会拒收的病（`not_in_candidates` / `voice_disease_conflict`），
   * 纸上却照样写着它——界面停在一个自相矛盾的状态上。⇒ 不在候选里就退回没认（诊断栏随之回到空白态）。
   * 这与退役前那个模块的 `reconcileDiseases()` 是同一条口径（换答案 → 退掉池外的条目）。
   */
  function reconcileDisease() {
    const id = confirmedId()
    if (!id) return
    if (!candidateState().candidates.some((c) => c.id === id)) state.disease = null
  }

  function commitMulti(question) {
    const limit = answerLimitOf(clinic, question)
    const draft = Array.isArray(state.answers[question.id]) ? [...state.answers[question.id]] : []
    state.answers = { ...state.answers, [question.id]: draft }
    if (draft.length < limit.min) { setMessage(ui.status_answering); return render() }
    const { state: next, dropped } = applyAnswer(clinic, state, question.id, draft)
    state.answers = next.answers
    afterAnswer(dropped)
    render()
  }

  function commitMultiForce(question) {
    const value = state.answers[question.id]
    const { state: next, dropped } = applyAnswer(clinic, state, question.id, value)
    state.answers = next.answers
    afterAnswer(dropped)
    render()
  }

  function onAnswer(valueId) {
    const question = current()
    if (!question) return
    if (isMulti(clinic, question)) {
      const limit = answerLimitOf(clinic, question)
      const draft = Array.isArray(state.answers[question.id]) ? [...state.answers[question.id]] : []
      const at = draft.indexOf(valueId)
      if (isRefuse(clinic, valueId)) {
        state.answers = { ...state.answers, [question.id]: [valueId] }
        return commitMultiForce(question)
      }
      const cleaned = draft.filter((v) => !isRefuse(clinic, v))
      if (at >= 0) cleaned.splice(cleaned.indexOf(valueId), 1)
      else if (cleaned.length < limit.max) cleaned.push(valueId)
      state.answers = { ...state.answers, [question.id]: cleaned }
      return commitMulti(question)
    }
    const { state: next, dropped } = applyAnswer(clinic, state, question.id, valueId)
    state.answers = next.answers
    afterAnswer(dropped)
    render()
  }

  function onCommit() {
    const question = current()
    if (!question) return
    const limit = answerLimitOf(clinic, question)
    const draft = state.answers[question.id]
    if (!Array.isArray(draft) || draft.length < limit.min) return
    const { state: next, dropped } = applyAnswer(clinic, state, question.id, draft)
    state.answers = next.answers
    afterAnswer(dropped)
    render()
  }

  /**
   * 「认」这一支笔（阶段 7）：从候选里认下其中一张；**再点同一张 = 反悔**（退回没认的状态）。
   *
   * 拒绝码有两道，都是**兜底判据**：`not_in_candidates`（候选由数据算出来，界面上点不到候选以外的病）
   * 与 `voice_disease_conflict`（数据自洽时「先收窄后落笔」让这道判据永不触发，见口径文档 §3.2）。
   * 真被拒时把世界下沿那句状态换成数据里的「你说话的样子，已经把你带到「X」这一张上了」——
   * 依然不新增任何中文文案字面量。
   */
  function onConfirmDisease(diseaseId) {
    const target = confirmedId() === diseaseId ? null : diseaseId
    const { state: next, rejected } = confirmDisease(clinic, opening, diseases, state, target)
    if (rejected) {
      const voiced = clinic.voices.items.find((v) => v.id === tally().dominant)
      const label = voiced?.disease ? diseaseLabelOf(voiced.disease) : null
      setMessage(label ? copy(wiring.candidate_narrowed, { label }) : state.message)
      return render()
    }
    state.disease = next.disease
    setMessage(ui.status_ready_sign)
    render()
  }

  function onBack() {
    const ids = Object.keys(state.answers)
    if (!ids.length) return
    const ordered = [...clinic.questions].map((q) => q.id).filter((id) => ids.includes(id))
    const last = ordered[ordered.length - 1]
    const { state: next } = reAnswer(clinic, state, last)
    state.answers = next.answers
    state.signed = false
    reconcileDisease()
    setMessage(ui.restart_hint)
    render()
  }

  function onReanswer(questionId) {
    const { state: next } = reAnswer(clinic, state, questionId)
    state.answers = next.answers
    state.signed = false
    reconcileDisease()
    setMessage(ui.restart_hint)
    render()
  }

  function onClick(event) {
    const target = event.target
    const disease = target.closest('[data-disease]')
    if (disease) return onConfirmDisease(disease.dataset.disease)
    const answer = target.closest('[data-answer-value]')
    if (answer) return onAnswer(answer.dataset.answerValue)
    if (target.closest('[data-answer-commit]')) return onCommit()
    const re = target.closest('[data-reanswer]')
    if (re) return onReanswer(re.dataset.reanswer)
    if (target.closest('[data-ask-back]')) return onBack()
    const field = target.closest('[data-character-field]')
    if (field) {
      const { characterField, characterValue } = field.dataset
      if (characterField === 'surname') state.surname = state.surname === characterValue ? null : characterValue
      else if (characterField === 'given') state.given = state.given === characterValue ? null : characterValue
      else if (characterField === 'gender') state.gender = state.gender === characterValue ? null : characterValue
      return render()
    }
    const source = target.closest('[data-character-source]')
    if (source) {
      state.characterSource = source.dataset.characterSource
      if (!isCustom()) { state.surname = null; state.given = null; state.gender = null }
      return render()
    }
    if (target.closest('[data-sign]')) {
      state.signed = true
      setMessage(ui.status_signed)
      notify()
      return render()
    }
    if (target.closest('[data-confirm]')) return close(true)
    if (target.closest('[data-close]') && !required) return close(false)
  }

  /** 数字键 = 挑选那一句（叙事界面布局 §四 第 2 条：当前选项支持数字键选择）。 */
  function onKeydown(event) {
    if (!state.open || event.metaKey || event.ctrlKey || event.altKey) return
    if (event.key === 'Backspace') { event.preventDefault(); return onBack() }
    if (!/^[1-9]$/.test(event.key)) return
    const button = shell.querySelector ? shell.querySelector(`[data-choice-index="${event.key}"]`) : null
    if (!button) return
    event.preventDefault()
    // 候选那一拍的数字键走的是「认」，不是「答」（两者都挂在 data-choice-index 上）。
    if (button.dataset.disease) return onConfirmDisease(button.dataset.disease)
    onAnswer(button.dataset.answerValue)
  }

  root.addEventListener('click', onClick)
  document.addEventListener('keydown', onKeydown)

  function open() {
    state.open = true
    root.hidden = false
    document.documentElement.classList.add('oc-open')
    setMessage(ui.status_answering)
    render()
    notify()
  }

  function close(done = false) {
    state.open = false
    state.completed = state.completed || done
    root.hidden = true
    document.documentElement.classList.remove('oc-open')
  }

  state.completed = false

  if (trigger) {
    trigger.addEventListener('click', () => open())
    trigger.textContent = trigger.textContent || ui.launch
  }

  return {
    open,
    close: () => close(false),
    subscribe(listener) { listeners.add(listener); return () => listeners.delete(listener) },
    getProfile: () => profileOf(clinic, state, { character: character() }),
    get completed() { return state.completed },
    get state() { return state },
    render,
  }
}

export { chiefComplaint }
