// 地图人物对话浮层。
//
// 来源：design/presentation/500床一层跑团地图原型.md §2.4（owner 2026-09-23 口径：
// 点击地图上的人物要像开局探索那样有一套自己的显示界面）。
//
// 这一层只负责呈现与转发：对话内容、层级、选项与效果全部由 dialogue-runtime 求值，
// 浮层不得自己判断条件、自己写状态，也不得与右侧叙事面板出现两套真相。因此它只
// 调用注入的 dialogue 门面（selectNpc / view / choose / leave / subscribe），并把
// 每次 view 变化重新渲染一次。
//
// 会话结束时（选项带 end）runtime 会清空 session。按[场景化对话与任务写作方法]
// §八「连续记录」，浮层不能因此把刚读过的文本清掉，所以这里保留一份收束快照。

const escapeHtml = value => String(value)
  .replaceAll('&', '&amp;')
  .replaceAll('<', '&lt;')
  .replaceAll('>', '&gt;')
  .replaceAll('"', '&quot;')

// 来源：design/events/游戏循环.md §2.2（时段闭集）。
const timeLabels = { morning: '上午', afternoon: '下午', night: '夜晚' }

// 与右侧叙事面板保持同一套块类型标签，避免同一段文本在两处有不同名字。
const blockLabels = {
  description: '场景',
  player: '你',
  experience: '经历影响',
  disease: '疾病影响',
  evidence: '物证',
}

function blockHtml(block) {
  const label = block.source || block.speaker || blockLabels[block.kind] || '叙述'
  const form = block.form ? ` ${block.form}` : ''
  return `<article class="md-beat ${escapeHtml(block.kind)}${form}">
    <div class="md-label">${escapeHtml(label)}</div>
    <p>${escapeHtml(block.text).replaceAll('\n', '<br>')}</p>
  </article>`
}

function factHtml(label, value) {
  if (!value) return ''
  return `<div class="md-fact"><span>${escapeHtml(label)}</span><b>${escapeHtml(value)}</b></div>`
}

function sceneHtml(npc, context, session) {
  const time = context.time
  return `<section class="md-scene" aria-label="${escapeHtml(npc.name)}">
    <div class="md-backdrop" aria-hidden="true"></div>
    <div class="md-figure" aria-hidden="true"><i></i><b>${escapeHtml(npc.mark)}</b></div>
    <header>
      <span>${escapeHtml(context.locationLabel || '住院楼 · 一层')}</span>
      <h1>${escapeHtml(npc.name)}</h1>
      <p>${escapeHtml(npc.role)}${npc.identityKnown ? '' : ' · 身份尚未确认'}</p>
    </header>
    <aside class="md-facts" aria-label="此刻的位置与状态">
      ${factHtml('待的地方', context.locationLabel || '住院楼一层')}
      ${factHtml('时段', timeLabels[time] || time)}
      ${factHtml('正在做', context.activity)}
      ${factHtml('关系', npc.relationLabel)}
      ${factHtml('对话层', session ? session.depthLabel : npc.depthLabel)}
    </aside>
    <p class="md-description">${escapeHtml(npc.description)}</p>
    ${context.basis ? `<p class="md-basis" aria-label="落位依据">${escapeHtml(context.basis)}</p>` : ''}
    <p class="md-identity-note">${npc.identityKnown
      ? '这个人愿意让你知道他是谁。'
      : '你还不知道这个人是谁。名字与身份要在交谈或院内记录里取得。'}</p>
    <p class="md-prototype-note">原型口径：一层还没有玩家坐标，所以这里不做"必须与人物在同一地点才能交谈"的距离判定。</p>
  </section>`
}

function footerHtml({ options, hasSession, ended }) {
  if (options.length) {
    return `<div class="md-actions">${options.map((option, index) => `<button type="button" data-md-choice="${escapeHtml(option.id)}">
      <i>${String(index + 1).padStart(2, '0')}</i><span>${escapeHtml(option.text)}<small>${escapeHtml(option.meta || '')}</small></span>
    </button>`).join('')}</div>`
  }
  const label = ended ? '站起身，走开' : hasSession ? '结束这次交谈' : '先不打扰'
  const meta = ended ? '这次谈话到此为止' : hasSession ? '离开当前对话层' : '回到地图'
  return `<div class="md-actions"><button type="button" data-md-action="close"><i>01</i><span>${label}<small>${meta}</small></span></button></div>`
}

function narrativeHtml(npc, state) {
  const { session, transcript, options, note, ended } = state
  const subtitle = session ? `${session.depthLabel} · ${options.length} 个回应` : ended ? '记录到此为止' : '此刻无法交谈'
  return `<aside class="md-narrative" aria-label="对话记录">
    <header>
      <span>DIALOGUE · 住院楼一层</span>
      <h2>${escapeHtml(session?.objective || state.objective || npc.objective)}</h2>
      <p>${escapeHtml(subtitle)}</p>
    </header>
    <div class="md-transcript" data-md-transcript>${
      transcript.length
        ? transcript.map(blockHtml).join('')
        : '<article class="md-beat description"><div class="md-label">等待</div><p>这里还没有可读的记录。</p></article>'
    }${note ? `<article class="md-beat md-note"><div class="md-label">当前所知</div><p>${escapeHtml(note)}</p></article>` : ''}</div>
    <footer>${footerHtml({ options, hasSession: Boolean(session), ended })}</footer>
  </aside>`
}

export function createDialogueOverlay({ dialogue, mount = document.body } = {}) {
  const element = document.createElement('section')
  element.className = 'md-overlay'
  element.hidden = true
  element.setAttribute('role', 'dialog')
  element.setAttribute('aria-modal', 'true')
  element.setAttribute('aria-label', '地图人物对话')
  mount.append(element)

  let openNpcId = null
  let openContext = {}
  // 会话结束后的收束快照：保留最后读到的连续记录，不清空前文。
  let closing = null

  function render() {
    if (element.hidden || !openNpcId) return
    const npc = dialogue.dossier(openNpcId)
    if (!npc) return
    const session = dialogue.view().session
    const useClosing = !session && closing?.npcId === openNpcId
    const transcript = session
      ? session.transcript
      : useClosing
        ? closing.transcript
        : npc.dossier.map(fact => ({ kind: 'dossier-fact', source: fact.label, text: `${fact.text}（来源：${fact.source}）` }))
    const options = session ? session.options : []
    const note = session ? null : useClosing ? '这次谈话已经结束；关系与线索留在记录里。' : (npc.lockedHint || '现在还不是说话的时候。')
    element.innerHTML = `<main class="md-shell">
      ${sceneHtml(npc, openContext, session)}
      ${narrativeHtml(npc, { session, transcript, options, note, ended: useClosing, objective: closing?.npcId === openNpcId ? closing.objective : null })}
    </main>`
    window.requestAnimationFrame(() => {
      const scroller = element.querySelector('[data-md-transcript]')
      if (scroller) scroller.scrollTop = scroller.scrollHeight
    })
  }

  function open(npcId, context = {}) {
    openNpcId = npcId
    openContext = context
    closing = null
    dialogue.selectNpc(npcId, { nearby: true, locationId: context.locationId || null, activity: context.activity || null })
    element.hidden = false
    document.documentElement.classList.add('md-open')
    render()
  }

  function close() {
    if (element.hidden) return
    element.hidden = true
    openNpcId = null
    closing = null
    document.documentElement.classList.remove('md-open')
    // 玩家主动离开：已经发生的微反应与关系变化留在运行时，下次交互重新求值入口。
    dialogue.leave()
  }

  element.addEventListener('click', event => {
    const choice = event.target.closest('[data-md-choice]')
    if (choice) {
      const before = dialogue.view().session
      const option = before?.options.find(item => item.id === choice.dataset.mdChoice)
      dialogue.choose(choice.dataset.mdChoice)
      if (!dialogue.view().session && before && option) {
        closing = {
          npcId: openNpcId,
          objective: before.objective,
          transcript: [...before.transcript, { kind: 'player', speaker: '你', text: option.text }],
        }
      }
      render()
      return
    }
    if (event.target.closest('[data-md-action="close"]')) close()
  })

  document.addEventListener('keydown', event => {
    if (element.hidden) return
    if (event.key === 'Escape') {
      event.preventDefault()
      close()
      return
    }
    // 浮层打开时，快捷输入属于浮层；不要让底下的地图或开发者快捷键抢走。
    event.stopImmediatePropagation()
  }, true)

  dialogue.subscribe(() => render())

  return {
    open,
    close,
    render,
    isOpen: () => !element.hidden,
    npcId: () => openNpcId,
    element,
  }
}
