import {
  createOpeningState,
  dispatchOpening,
  openingActions,
  openingHotspots,
} from './opening-runtime.js'

const escapeHtml = value => String(value)
  .replaceAll('&', '&amp;')
  .replaceAll('<', '&lt;')
  .replaceAll('>', '&gt;')
  .replaceAll('"', '&quot;')

function blockHtml(item) {
  if (item.kind === 'check') {
    return `<article class="oe-beat oe-check ${item.success ? 'success' : 'failure'}">
      <div class="oe-label"><span>${escapeHtml(item.label)}</span><b>${escapeHtml(item.text)}</b></div>
      <p>${escapeHtml(item.detail)}</p>
      <small>${escapeHtml(item.attribute)} ${item.score} / 需要 ${item.threshold}</small>
    </article>`
  }
  return `<article class="oe-beat ${escapeHtml(item.kind)}">
    <div class="oe-label">${escapeHtml(item.label)}</div>
    <p>${escapeHtml(item.text).replaceAll('\n', '<br>')}</p>
  </article>`
}

function stageHtml(state) {
  if (state.phase === 'moon') return `
    <div class="oe-city"></div>
    <button class="oe-moon" type="button" data-opening-action="inspect_moon" aria-label="仔细观察圆月"><i></i><span>圆月</span></button>
    <div class="oe-silhouette waiting"></div>`

  if (state.phase === 'boundary') return `
    <div class="oe-black-boundary"></div>
    <div class="oe-road"><i></i><i></i><i></i></div>
    <div class="oe-hospital"><span>　　精神卫生中心</span></div>
    <div class="oe-silhouette boundary"></div>
    ${openingHotspots(state).map(hotspot => `<button class="oe-hotspot ${hotspot.position}${hotspot.visited ? ' visited' : ''}" type="button"
      data-opening-action="${hotspot.id}" ${hotspot.disabled ? 'disabled' : ''}>
      <i></i><span>${escapeHtml(hotspot.label)}</span>
    </button>`).join('')}`

  if (state.phase === 'daylight') return `
    <div class="oe-daylight"></div>
    <div class="oe-hospital daylight"><span>　　精神卫生中心</span></div>
    <div class="oe-figures"><i></i><i></i></div>
    <div class="oe-silhouette daylight"></div>`

  return `
    <div class="oe-daylight complete"></div>
    <div class="oe-wristband"><small>PATIENT</small><b>苟笙</b><span>0527</span><em>B 栋 147 室 4 床</em></div>`
}

function phaseTitle(state) {
  if (state.phase === 'moon') return ['公司楼下·等车点', '月初的圆月']
  if (state.phase === 'boundary') return ['精神卫生中心·大门外', '找到来时的路']
  if (state.phase === 'daylight') return ['门诊楼·台阶', '“找到了”']
  return ['B 栋·147 室', '姓名：苟笙']
}

export function createOpeningExploration({ onComplete } = {}) {
  let state = null
  const root = document.createElement('section')
  root.className = 'oe-overlay'
  root.hidden = true
  root.setAttribute('aria-label', '主角入院序章')
  document.body.append(root)

  function render() {
    if (!state) return
    const [kicker, title] = phaseTitle(state)
    const actions = openingActions(state)
    root.innerHTML = `
      <main class="oe-shell phase-${state.phase}">
        <section class="oe-scene" aria-label="${escapeHtml(title)}">
          ${stageHtml(state)}
          <header><span>${escapeHtml(kicker)}</span><h1>${escapeHtml(title)}</h1></header>
          <aside class="oe-attributes" aria-label="开局属性">
            ${Object.entries(state.attributes).map(([name, value]) => `<span>${escapeHtml(name)}<b>${value.points}</b><small>${escapeHtml(value.level)}</small></span>`).join('')}
          </aside>
          ${state.phase === 'boundary' ? '<p class="oe-explore-hint">点击现场中的标记自由调查。绕行和投石后，你才能真正决定走向哪里。</p>' : ''}
        </section>
        <aside class="oe-narrative">
          <header><span>PROLOGUE · 00</span><h2>一个普通人进入治疗中心</h2><p>原稿文本 + 探索 / 检定原型</p></header>
          <div class="oe-transcript" data-opening-transcript>${state.transcript.map(blockHtml).join('')}</div>
          <footer>
            ${actions.length ? `<div class="oe-actions">${actions.map((action, index) => `<button type="button" data-opening-action="${action.id}">
              <i>${String(index + 1).padStart(2, '0')}</i><span>${escapeHtml(action.label)}<small>${escapeHtml(action.meta)}</small></span>
            </button>`).join('')}</div>` : '<p>请在左侧现场中选择调查点。</p>'}
          </footer>
        </aside>
      </main>`
    window.requestAnimationFrame(() => {
      const transcript = root.querySelector('[data-opening-transcript]')
      if (transcript) transcript.scrollTop = transcript.scrollHeight
    })
  }

  function open(profile) {
    state = createOpeningState(profile)
    root.hidden = false
    document.documentElement.classList.add('oe-open')
    render()
  }

  function finish() {
    root.hidden = true
    document.documentElement.classList.remove('oe-open')
    onComplete?.(state)
  }

  root.addEventListener('click', event => {
    const action = event.target.closest('[data-opening-action]')?.dataset.openingAction
    if (!action) return
    if (action === 'finish') return finish()
    dispatchOpening(state, action)
    render()
  })

  document.addEventListener('keydown', event => {
    if (root.hidden) return
    event.stopImmediatePropagation()
  }, true)

  return { open, finish, get state() { return state } }
}

