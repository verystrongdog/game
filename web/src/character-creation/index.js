import {
  attributeDescriptions,
  attributeNames,
  developmentDefaultCharacter,
  developmentalDiseases,
  diseases,
  experienceCategories,
} from './character-data.js'
import {
  EXPERIENCE_LIMIT,
  calculateAttributes,
  getDiseaseCandidates,
  getExperience,
  getUnresolvedDiseaseCandidates,
  isDiseaseAvailable,
  selectionBlockReason,
} from './character-model.js'

const steps = ['经历', '属性', '候选', '选择', '镜子']
const escapeHtml = value => String(value)
  .replaceAll('&', '&amp;')
  .replaceAll('<', '&lt;')
  .replaceAll('>', '&gt;')
  .replaceAll('"', '&quot;')

function attributeText(attributes) {
  return Object.entries(attributes).map(([name, amount]) => `${name} ${amount >= 0 ? '+' : ''}${amount}`).join(' · ')
}

function diseaseCard(disease, { selectable = false, selected = false, developmental = false } = {}) {
  const tag = developmental ? '<span class="cc-tag congenital">生来的</span>' : ''
  return `
    <${selectable ? 'button' : 'article'} class="cc-disease-card${selected ? ' selected' : ''}"
      ${selectable ? `type="button" data-disease="${escapeHtml(disease.name)}" aria-pressed="${selected}"` : ''}>
      <div class="cc-card-heading">
        <div><span class="cc-form">${escapeHtml(disease.form)}</span>${tag}</div>
        ${selectable ? `<span class="cc-check">${selected ? '已选择' : '选择'}</span>` : ''}
      </div>
      <h3>${escapeHtml(disease.name)}</h3>
      <p class="cc-flavor">${escapeHtml(disease.flavor)}</p>
      <dl>
        <div><dt>情境</dt><dd>${escapeHtml(disease.bonus)}</dd></div>
        <div class="open"><dt>打开</dt><dd>${escapeHtml(disease.opens)}</dd></div>
        <div class="closed"><dt>关闭</dt><dd>${escapeHtml(disease.closes)}</dd></div>
        <div><dt>代价</dt><dd>${escapeHtml(disease.cost)}</dd></div>
      </dl>
    </${selectable ? 'button' : 'article'}>`
}

export function createCharacterCreation({ trigger, required = false }) {
  const profileListeners = new Set()
  const state = {
    open: false,
    step: 0,
    categoryId: experienceCategories[0].id,
    selectedExperiences: new Set(),
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

  function eligibleDiseases() {
    return diseases.filter(disease => isDiseaseAvailable(disease.name, state.selectedExperiences))
  }

  function reconcileDiseases() {
    for (const name of state.selectedDiseases) {
      if (!isDiseaseAvailable(name, state.selectedExperiences)) state.selectedDiseases.delete(name)
    }
  }

  function profile() {
    return {
      id: 'character_creation',
      label: '开局人物',
      experiences: [...state.selectedExperiences],
      diseases: [...state.selectedDiseases],
    }
  }

  function notifyProfile() {
    const value = profile()
    profileListeners.forEach(listener => listener(value))
  }

  function renderExperienceStep() {
    const category = experienceCategories.find(item => item.id === state.categoryId)
    const attributes = calculateAttributes(state.selectedExperiences)
    return `
      <div class="cc-experience-layout">
        <nav class="cc-category-list" aria-label="经历类别">
          ${experienceCategories.map(item => {
            const count = item.experiences.filter(exp => state.selectedExperiences.has(exp.id)).length
            return `<button type="button" data-category="${item.id}" class="${item.id === category.id ? 'active' : ''}">
              <span>${item.title}</span><small>${count} / 2</small>
            </button>`
          }).join('')}
        </nav>
        <section class="cc-experience-main">
          <div class="cc-category-intro"><div><span>${category.parent}</span><h2>${category.title}</h2></div><blockquote>“${category.quote}”</blockquote></div>
          <div class="cc-experience-grid">
            ${category.experiences.map(experience => {
              const selected = state.selectedExperiences.has(experience.id)
              const reason = selectionBlockReason(state.selectedExperiences, experience.id)
              return `<button type="button" class="cc-experience-card${selected ? ' selected' : ''}${reason ? ' blocked' : ''}"
                data-experience="${experience.id}" aria-pressed="${selected}" aria-disabled="${Boolean(reason)}">
                <span class="cc-card-index">${selected ? '✓' : String(category.experiences.indexOf(experience) + 1).padStart(2, '0')}</span>
                <span class="cc-experience-copy">
                  <b>${escapeHtml(experience.label)}</b>
                  <span>${escapeHtml(experience.description)}</span>
                  <small class="gain">属性变化 · ${attributeText(experience.attributes)}</small>
                  <small class="burden">负担提案（未接入游戏） · ${escapeHtml(experience.burden)}</small>
                </span>
                <span class="cc-art-slot" aria-hidden="true"></span>
                ${reason ? `<span class="cc-block-reason">${escapeHtml(reason)}</span>` : ''}
              </button>`
            }).join('')}
          </div>
        </section>
        <aside class="cc-live-summary">
          <span class="cc-kicker">正在形成</span>
          <strong>${state.selectedExperiences.size} / ${EXPERIENCE_LIMIT}</strong>
          <p>经历决定属性，也决定哪些疾病会成为候选。</p>
          <div class="cc-mini-attributes">
            ${attributeNames.map(name => `<div><span>${name}</span><b>${attributes[name].level}</b><i style="--level:${attributes[name].points}"></i></div>`).join('')}
          </div>
        </aside>
      </div>`
  }

  function renderAttributeStep() {
    const attributes = calculateAttributes(state.selectedExperiences)
    return `
      <section class="cc-centered cc-attributes-screen">
        <span class="cc-kicker">经历留下的东西</span>
        <h2>这不是你分配的点数。</h2>
        <p class="cc-lead">你做过什么，就练出了什么。每段经历的属性变化净值固定为 +2，少数经历会用 +3/−1 留下真实代价；5–6 点是“精通”，只有 10 点才是“本能”。</p>
        <div class="cc-attribute-grid">
          ${attributeNames.map(name => {
            const value = attributes[name]
            const sources = [...state.selectedExperiences].map(getExperience).filter(exp => exp?.attributes[name])
            return `<article class="cc-attribute-card">
              <div class="cc-attribute-art" aria-hidden="true"></div>
              <div class="cc-attribute-heading"><span>${name}</span><em>${value.points} / 10</em></div>
              <strong>${value.level}</strong>
              <div class="cc-pips">${Array.from({ length: 10 }, (_, index) => index + 1).map(point => `<i class="${point <= value.points ? 'on' : ''}"></i>`).join('')}</div>
              <p class="cc-ability">${escapeHtml(attributeDescriptions[name][value.level])}</p>
              <small class="cc-attribute-sources">${sources.length ? sources.map(exp => {
                const amount = exp.attributes[name]
                return `${escapeHtml(exp.label)}（${amount >= 0 ? '+' : ''}${amount}）`
              }).join(' · ') : '没有经历为这一项留下痕迹'}</small>
            </article>`
          }).join('')}
        </div>
      </section>`
  }

  function renderCandidateStep() {
    const candidates = getDiseaseCandidates(state.selectedExperiences)
    const unresolved = getUnresolvedDiseaseCandidates(state.selectedExperiences)
    const developmental = diseases.filter(disease => developmentalDiseases.has(disease.name))
    return `
      <section class="cc-candidates-screen">
        <div class="cc-section-heading">
          <div><span class="cc-kicker">经历轨</span><h2>这些是可能长出来的形状。</h2></div>
          <p>${candidates.length} 个候选由你的经历解锁。经历只把门打开；要不要让它成为病，下一步由你选择。</p>
        </div>
        ${unresolved.length ? `<div class="cc-design-warning"><b>设计映射待核</b><span>${unresolved.map(escapeHtml).join('、')} 出现在所选经历的映射中，但不在 26 病总表内；原型不擅自生成疾病卡。</span></div>` : ''}
        <div class="cc-disease-grid">${candidates.map(disease => diseaseCard(disease)).join('')}</div>
        <div class="cc-developmental">
          <div><span class="cc-kicker">发育轨 · 独立一屏</span><h2>有些东西不是后来发生的。</h2><p>ASD 与 ADHD 不由经历产生，始终作为独立候选出现。</p></div>
          <div class="cc-disease-grid">${developmental.map(disease => diseaseCard(disease, { developmental: true })).join('')}</div>
        </div>
      </section>`
  }

  function renderDiseaseStep() {
    return `
      <section class="cc-candidates-screen">
        <div class="cc-section-heading">
          <div><span class="cc-kicker">你自己的选择</span><h2>要不要让它变成病？</h2></div>
          <p>一个病都不选是合法的。设计尚未确定最多能选几种，因此本原型不设上限；这不是正式规则。</p>
        </div>
        <div class="cc-selection-count"><b>${state.selectedDiseases.size}</b><span>已选择<br>数量待定</span></div>
        <div class="cc-disease-grid selectable">
          ${eligibleDiseases().map(disease => diseaseCard(disease, {
            selectable: true,
            selected: state.selectedDiseases.has(disease.name),
            developmental: developmentalDiseases.has(disease.name),
          })).join('')}
        </div>
      </section>`
  }

  function renderMirrorStep() {
    const attributes = calculateAttributes(state.selectedExperiences)
    const selected = diseases.filter(disease => state.selectedDiseases.has(disease.name))
    const remaining = EXPERIENCE_LIMIT - state.selectedExperiences.size
    return `
      <section class="cc-mirror-screen">
        <div class="cc-mirror-visual" aria-hidden="true"><div class="cc-mask-preview"><i></i></div><span>面具先替你露面。外观整理尚未实现。</span></div>
        <div class="cc-final-summary">
          <span class="cc-kicker">开局预览</span>
          <h2>${selected.length ? '你决定带着这些走。' : '你什么都没选。'}</h2>
          <p>${selected.length
            ? '经历决定你有什么；疾病决定你让什么成为自己的一部分。'
            : '你没有病。你也没有任何东西可以拿来对付这个地方。在这个楼层里，这两句话是同一句话。'}</p>
          <div class="cc-final-attributes">${attributeNames.map(name => `<span>${name}<b>${attributes[name].level}</b></span>`).join('')}</div>
          <div class="cc-final-diseases">
            ${selected.length ? selected.map(disease => `<article><span>${disease.form}</span><h3>${disease.name}</h3><p>${disease.flavor}</p></article>`).join('') : '<div class="cc-normal-build">零疾病 · 没有可被针对的模式，也没有疾病打开的门。</div>'}
          </div>
          ${remaining > 0
            ? `<button type="button" class="cc-enter incomplete" data-step="0">还有 ${remaining} 段经历未使用 · 返回选择</button>`
            : '<button type="button" class="cc-enter" data-confirm>确认人物并进入序章</button>'}
          <small>确认后，经历与疾病会交给本页对话原型；刷新页面仍会重新开局，不写入正式游戏存档。疾病挂件、花纹与裂隙的整理编辑器为低优先级，暂未实现。</small>
        </div>
      </section>`
  }

  function bodyForStep() {
    return [renderExperienceStep, renderAttributeStep, renderCandidateStep, renderDiseaseStep, renderMirrorStep][state.step]()
  }

  function render() {
    const remaining = EXPERIENCE_LIMIT - state.selectedExperiences.size
    shell.innerHTML = `
      <header class="cc-header">
        <div><span class="cc-kicker">CHARACTER ORIGIN · INTERACTION PROTOTYPE</span><h1 id="ccTitle">开局人物</h1></div>
        <ol>${steps.map((step, index) => `<li class="${index === state.step ? 'active' : ''}${index < state.step ? 'done' : ''}"><button type="button" data-step="${index}" aria-label="查看${step}"><i>${String(index + 1).padStart(2, '0')}</i><span>${step}</span></button></li>`).join('')}</ol>
        ${required && !state.completed
          ? '<span class="cc-required">完成人物选择后进入序章</span>'
          : '<button type="button" class="cc-close" data-close aria-label="关闭开局人物界面">×</button>'}
      </header>
      <main class="cc-body">
        ${remaining > 0 && state.step > 0 ? `<div class="cc-unused-warning">预览模式 · 还有 <b>${remaining}</b> 段经历未使用，候选与属性会继续变化。</div>` : ''}
        ${bodyForStep()}
      </main>
      <footer class="cc-footer">
        <div class="cc-status" role="status" aria-live="polite">${escapeHtml(state.message || (remaining > 0 ? `还有 ${remaining} 段经历未使用 · 可以先查看后续` : '经历已选满 · 可以确认预览'))}</div>
        <div>
          ${import.meta.env.DEV && required && !state.completed ? '<button type="button" class="cc-dev-default" data-dev-default>开发默认人物 · 直接进入</button>' : ''}
          ${state.step > 0 ? '<button type="button" class="cc-secondary" data-back>上一步</button>' : '<button type="button" class="cc-secondary" data-reset>清空</button>'}
          ${state.step < steps.length - 1 ? '<button type="button" class="cc-primary" data-next>继续预览</button>' : ''}
        </div>
      </footer>`
  }

  function open() {
    state.open = true
    root.hidden = false
    document.documentElement.classList.add('cc-open')
    render()
    ;(shell.querySelector('.cc-close') || shell.querySelector('[data-step]'))?.focus()
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

  root.addEventListener('click', event => {
    const closeButton = event.target.closest('[data-close]')
    if (closeButton) return close()

    if (event.target.closest('[data-confirm]')) {
      if (state.selectedExperiences.size < EXPERIENCE_LIMIT) {
        state.message = `还有 ${EXPERIENCE_LIMIT - state.selectedExperiences.size} 段经历未使用。`
        state.step = 0
        return render()
      }
      state.completed = true
      state.message = '开局人物已确认。'
      notifyProfile()
      render()
      return close()
    }

    if (event.target.closest('[data-dev-default]')) {
      state.selectedExperiences = new Set(developmentDefaultCharacter.experiences)
      state.selectedDiseases = new Set(developmentDefaultCharacter.diseases)
      state.completed = true
      state.step = steps.length - 1
      state.message = '已使用开发默认人物。'
      notifyProfile()
      render()
      return close()
    }

    const categoryButton = event.target.closest('[data-category]')
    if (categoryButton) {
      state.categoryId = categoryButton.dataset.category
      state.message = ''
      return render()
    }

    const experienceButton = event.target.closest('[data-experience]')
    if (experienceButton) {
      const id = experienceButton.dataset.experience
      if (state.selectedExperiences.has(id)) {
        state.selectedExperiences.delete(id)
        reconcileDiseases()
        state.message = '已移除这段经历。'
      } else {
        const reason = selectionBlockReason(state.selectedExperiences, id)
        if (reason) state.message = reason
        else {
          state.selectedExperiences.add(id)
          state.message = `已选择：${getExperience(id).label}`
        }
      }
      return render()
    }

    const diseaseButton = event.target.closest('[data-disease]')
    if (diseaseButton) {
      const name = diseaseButton.dataset.disease
      if (state.selectedDiseases.has(name)) state.selectedDiseases.delete(name)
      else state.selectedDiseases.add(name)
      state.message = state.selectedDiseases.has(name) ? `已选择：${name}` : `已移除：${name}`
      return render()
    }

    const stepButton = event.target.closest('[data-step]')
    if (stepButton) {
      state.step = Number(stepButton.dataset.step)
      state.message = ''
      shell.scrollTop = 0
      return render()
    }

    if (event.target.closest('[data-next]')) {
      state.step = Math.min(steps.length - 1, state.step + 1)
      state.message = ''
      shell.scrollTop = 0
      return render()
    }
    if (event.target.closest('[data-back]')) {
      state.step = Math.max(0, state.step - 1)
      state.message = ''
      shell.scrollTop = 0
      return render()
    }
    if (event.target.closest('[data-reset]')) {
      state.selectedExperiences.clear()
      state.selectedDiseases.clear()
      state.message = '已清空。'
      return render()
    }
  })

  root.addEventListener('click', event => {
    if (event.target === root) close()
  })

  document.addEventListener('keydown', event => {
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
