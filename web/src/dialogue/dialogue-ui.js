import { createDialogueRuntime } from './dialogue-runtime.js'
import { npcDialogues } from './npcs/index.js'
import { dialogueProfilePresets } from './profile-presets.js'

const escapeHtml = value => String(value)
  .replaceAll('&', '&amp;')
  .replaceAll('<', '&lt;')
  .replaceAll('>', '&gt;')
  .replaceAll('"', '&quot;')

const blockLabels = {
  description: '场景',
  player: '你',
  experience: '经历影响',
  disease: '疾病影响',
}

const timeLabels = {
  morning: '第 01 日<br>上午 · 人物交谈',
  afternoon: '第 01 日<br>下午 · 人物交谈',
  night: '第 01 日<br>夜晚 · 人物交谈',
}

// 来源：design/events/游戏循环.md §2.2；design/presentation/开局剧情逻辑原型.md §3.3。
const restLabels = {
  morning: '休息至下午',
  afternoon: '休息至夜晚',
  night: '休息至次日上午',
}

function restChoiceHtml(time) {
  return `<button class="choice" type="button" data-dialogue-rest><span class="choice-index">休</span><span>${restLabels[time]}<small class="choice-meta">推进时段，人物与环境会重新变化</small></span></button>`
}

function blockHtml(block) {
  const label = block.source || block.speaker || blockLabels[block.kind] || '叙述'
  const form = block.form ? ` ${block.form}` : ''
  return `<article class="beat dialogue-block ${escapeHtml(block.kind)}${form}">
    <div class="label">${escapeHtml(label)}</div>
    <p>${escapeHtml(block.text)}</p>
  </article>`
}

export function createDialogueUi() {
  const runtime = createDialogueRuntime({ npcDefinitions: npcDialogues })
  const subscribers = new Set()
  let pendingNpcContext = null
  const elements = {
    profiles: document.querySelector('#dialogueProfiles'),
    profileSummary: document.querySelector('#dialogueProfileSummary'),
    story: document.querySelector('#story'),
    choices: document.querySelector('#choices'),
    notes: document.querySelector('#dialogueNotes'),
    promise: document.querySelector('#dialoguePromise'),
    question: document.querySelector('#dialogueQuestion'),
    objective: document.querySelector('#objectiveText'),
    time: document.querySelector('#timeReadout'),
    speakerMark: document.querySelector('#speakerMark'),
    speakerRole: document.querySelector('#speakerRole'),
    speakerName: document.querySelector('#speakerName'),
    speakerDescription: document.querySelector('#speakerDescription'),
    scroll: document.querySelector('#storyScroll'),
  }

  function renderProfiles(view) {
    elements.profileSummary.textContent = `${view.profile.label} · ${view.profile.experiences.size} 段经历 · ${view.profile.diseases.size} 种疾病`
    elements.profiles.innerHTML = dialogueProfilePresets.map(profile => `
      <button type="button" data-dialogue-profile="${profile.id}" class="${view.profile.id === profile.id ? 'active' : ''}">
        ${escapeHtml(profile.label)}
      </button>`).join('')
  }

  function renderEmpty(view) {
    elements.speakerMark.textContent = '人'
    elements.speakerRole.textContent = '住院楼 · 等待接近人物'
    elements.speakerName.textContent = '附近没有正在交谈的人'
    elements.speakerDescription.textContent = '走到人物所在地点；足够近时，地图或三维场景才会给出交谈入口。'
    elements.objective.textContent = '在医院中靠近一名人物。'
    elements.story.innerHTML = `<article class="beat scene-text dialogue-lobby">
      <div class="label">距离限制</div>
      <p>对话不能从侧栏远程发起。二维地图需要与你处在同一地点；三维场景需要走进人物的近距离交互范围。</p>
    </article>`
    elements.choices.innerHTML = `<div class="choices-header"><span>等待交谈</span><span>先靠近人物</span></div>${restChoiceHtml(view.time)}`
  }

  function renderSession(view) {
    const session = view.session
    elements.speakerMark.textContent = session.npc.mark
    elements.speakerRole.textContent = `${session.npc.role} · ${session.depthLabel}`
    elements.speakerName.textContent = session.npc.name
    elements.speakerDescription.textContent = `${session.npc.description}${view.context.activity ? ` 此刻正在${view.context.activity}。` : ''}`
    elements.objective.textContent = session.objective
    elements.story.innerHTML = session.transcript.map(blockHtml).join('')
    elements.choices.innerHTML = `
      <div class="choices-header"><span>${escapeHtml(session.depthLabel)}对话</span><span>${session.options.length} 个回应</span></div>
      ${session.options.map((option, index) => `<button class="choice" type="button" data-dialogue-choice="${option.id}">
        <span class="choice-index">${String(index + 1).padStart(2, '0')}</span>
        <span>${escapeHtml(option.text)}<small class="choice-meta">${escapeHtml(option.meta || '')}</small></span>
      </button>`).join('')}`
  }

  function renderNotes(view) {
    elements.promise.innerHTML = `${escapeHtml(view.session?.objective || '认识住院楼里的人。')}<span>${view.session ? `${escapeHtml(view.session.npc.name)} · ${escapeHtml(view.session.depthLabel)}` : '选择人物后更新'}</span>`
    elements.notes.innerHTML = '<h2>线索</h2>' + (view.notes.length
      ? view.notes.map(note => `<div class="note-card">${escapeHtml(note.text)}<span>${escapeHtml(note.source)}</span></div>`).join('')
      : '<div class="note-card">尚未记录线索。<span>对话结果会留在这里</span></div>')
    elements.question.innerHTML = `${view.notes.length ? '这些记录是谁留下的，又是谁真正经历过？' : '谁愿意把自己的话留给你？'}<span>随对话推进变化</span>`
  }

  function render() {
    const view = runtime.view()
    renderProfiles(view)
    renderNotes(view)
    elements.time.innerHTML = timeLabels[view.time] || escapeHtml(view.time)
    if (view.session) renderSession(view)
    else renderEmpty(view)
    window.requestAnimationFrame(() => {
      elements.scroll.scrollTop = view.session ? elements.scroll.scrollHeight : 0
    })
    subscribers.forEach(listener => listener(view))
    return view
  }

  function showDossier(npcId, { coLocated = false, locationName = '医院一层', locationId = null, activity = null } = {}) {
    pendingNpcContext = { locationId, activity }
    const view = runtime.view()
    const npc = view.roster.find(item => item.id === npcId)
    if (!npc) return view
    document.querySelector('[data-view="story"]')?.click()
    renderNotes(view)
    elements.speakerMark.textContent = npc.displayMark
    elements.speakerRole.textContent = `人物档案 · ${locationName}`
    elements.speakerName.textContent = npc.displayName
    elements.speakerDescription.textContent = npc.identityKnown
      ? `${npc.displayRole}${activity ? `；正在${activity}` : ''}`
      : `你尚未从交谈或院内记录中得知这个人的身份。${activity ? `此人正在${activity}。` : ''}`
    elements.objective.textContent = coLocated ? `决定是否与${npc.displayName}交谈。` : `前往${locationName}后才能与此人交谈。`
    elements.story.innerHTML = npc.dossier.length
      ? npc.dossier.map(fact => `<article class="beat dossier-fact"><div class="label">${escapeHtml(fact.label)}</div><p>${escapeHtml(fact.text)}</p><small>${escapeHtml(fact.source)}</small></article>`).join('')
      : '<article class="beat dossier-empty"><div class="label">当前所知</div><p>你还没有获得可以写入人物档案的信息。</p></article>'
    elements.choices.innerHTML = coLocated && npc.available
      ? `<div class="choices-header"><span>人物互动</span><span>${escapeHtml(npc.relationLabel)}</span></div><button class="choice" type="button" data-dossier-chat="${npc.id}"><span class="choice-index">01</span><span>开始交谈<small class="choice-meta">进入当前可用的对话层</small></span></button>`
      : `<div class="choices-header"><span>人物互动</span><span>${coLocated ? '现在无法交谈' : '不在同一地点'}</span></div>`
    window.requestAnimationFrame(() => { elements.scroll.scrollTop = 0 })
    return view
  }

  elements.profiles.addEventListener('click', event => {
    const button = event.target.closest('[data-dialogue-profile]')
    const profile = dialogueProfilePresets.find(item => item.id === button?.dataset.dialogueProfile)
    if (profile) runtime.dispatch({ type: 'set_profile', profile })
    render()
  })
  elements.choices.addEventListener('click', event => {
    if (event.target.closest('[data-dialogue-rest]')) {
      runtime.dispatch({ type: 'rest' })
      render()
      return
    }
    const dossierChat = event.target.closest('[data-dossier-chat]')
    if (dossierChat) {
      runtime.dispatch({ type: 'select_npc', npcId: dossierChat.dataset.dossierChat, context: pendingNpcContext })
      render()
      return
    }
    const button = event.target.closest('[data-dialogue-choice]')
    if (!button) return
    runtime.dispatch({ type: 'choose', optionId: button.dataset.dialogueChoice })
    render()
  })

  render()

  return {
    restore: render,
    dossier(npcId) {
      return runtime.view().roster.find(item => item.id === npcId)
    },
    showDossier,
    subscribe(listener) {
      subscribers.add(listener)
      return () => subscribers.delete(listener)
    },
    showMapContext({ locationId = null, title, role = '一层地图 · 地点', mark = '图', description, detail, objective }) {
      pendingNpcContext = null
      runtime.dispatch({ type: 'set_context', context: { locationId } })
      elements.speakerMark.textContent = mark
      elements.speakerRole.textContent = role
      elements.speakerName.textContent = title
      elements.speakerDescription.textContent = description
      elements.objective.textContent = objective || `查看${title}。`
      elements.story.innerHTML = `<article class="beat scene-text"><div class="label">地点</div><p>${escapeHtml(detail || description)}</p></article>`
      elements.choices.innerHTML = `<div class="choices-header"><span>地图移动</span><span>选择左侧相邻活动点</span></div>${restChoiceHtml(runtime.view().time)}`
      window.requestAnimationFrame(() => { elements.scroll.scrollTop = 0 })
    },
    selectNpc(npcId, { nearby = false, locationId = null, activity = null } = {}) {
      if (!nearby) return runtime.view()
      runtime.dispatch({ type: 'select_npc', npcId, context: { locationId, activity } })
      return render()
    },
    setProfile(profile) {
      runtime.dispatch({ type: 'set_profile', profile })
      return render()
    },
    setTime(time) {
      runtime.dispatch({ type: 'set_time', time })
      return render()
    },
    view: runtime.view,
  }
}
