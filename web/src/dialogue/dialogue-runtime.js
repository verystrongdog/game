function hasAny(values, candidates = []) {
  return candidates.some(value => values.has(value))
}

function matches(requirements = {}, state, npcId) {
  const relation = state.relations[npcId] || 0
  if (requirements.met && !state.metNpcs.has(npcId)) return false
  if (requirements.metOrFlags && !state.metNpcs.has(npcId) && !hasAny(state.flags, requirements.metOrFlags)) return false
  if (requirements.times && !requirements.times.includes(state.time)) return false
  if (requirements.locations && !requirements.locations.includes(state.context.locationId)) return false
  if (requirements.activities && !requirements.activities.includes(state.context.activity)) return false
  if (requirements.allFlags?.some(flag => !state.flags.has(flag))) return false
  if (requirements.anyFlags && !hasAny(state.flags, requirements.anyFlags)) return false
  if (requirements.minRelation != null && relation < requirements.minRelation) return false
  if (requirements.experiencesAny && !hasAny(state.profile.experiences, requirements.experiencesAny)) return false
  if (requirements.diseasesAny && !hasAny(state.profile.diseases, requirements.diseasesAny)) return false
  return true
}

function unlockedLevels(npc, state) {
  return npc.levels.filter(level => matches(level.requires, state, npc.id))
}

function entryFor(level, state, npcId) {
  return level.entries?.find(entry => matches(entry.requires, state, npcId))?.node || level.entry
}

function visibleBlocks(node, state, npcId) {
  return (node?.blocks || []).filter(block => matches(block.requires, state, npcId))
}

function applyEffects(state, effects = {}, npcId) {
  effects.flagsAdd?.forEach(flag => state.flags.add(flag))
  effects.flagsRemove?.forEach(flag => state.flags.delete(flag))
  if (effects.relationDelta) {
    state.relations[npcId] = (state.relations[npcId] || 0) + effects.relationDelta
  }
  if (effects.time) state.time = effects.time
  effects.notes?.forEach(note => {
    if (!state.notes.some(existing => existing.id === note.id)) state.notes.push(note)
  })
}

const validTimes = new Set(['morning', 'afternoon', 'night'])
// 来源：design/events/游戏循环.md §2.2。
const nextRestTime = { morning: 'afternoon', afternoon: 'night', night: 'morning' }

export function createDialogueRuntime({ npcDefinitions, initialTime = 'morning' }) {
  const npcs = new Map(npcDefinitions.map(npc => [npc.id, npc]))
  const state = {
    time: initialTime,
    flags: new Set(),
    relations: {},
    metNpcs: new Set(),
    profile: { id: 'normal', label: '普通视角', experiences: new Set(), diseases: new Set() },
    context: { locationId: null, activity: null },
    session: null,
    notes: [],
  }

  function selectNpc(npcId, context = {}) {
    const npc = npcs.get(npcId)
    if (!npc) return
    state.context = { locationId: context.locationId || null, activity: context.activity || null }
    const levels = unlockedLevels(npc, state)
    const level = levels.at(-1)
    if (!level) return
    state.metNpcs.add(npcId)
    const situation = npc.situations?.find(entry => {
      const depths = entry.depths || ['surface']
      return depths.includes(level.id) && matches(entry.requires, state, npcId)
    })
    // 来源：design/events/剧情系统设计.md §3.8.2。
    state.session = { npcId, nodeId: situation?.node || entryFor(level, state, npcId), depth: level.id, history: [] }
  }

  function choose(optionId) {
    if (!state.session) return
    const npc = npcs.get(state.session.npcId)
    const node = npc?.nodes[state.session.nodeId]
    const option = node?.options?.find(item => item.id === optionId && matches(item.requires, state, npc.id))
    if (!option) return
    state.session.history.push(
      ...visibleBlocks(node, state, npc.id),
      { kind: 'player', speaker: '你', text: option.text },
    )
    applyEffects(state, option.effects, npc.id)
    if (option.end) state.session = null
    else if (option.next) state.session.nodeId = option.next
  }

  function setProfile(profile) {
    state.profile = {
      id: profile.id,
      label: profile.label,
      experiences: new Set(profile.experiences || []),
      diseases: new Set(profile.diseases || []),
    }
    state.session = null
  }

  function setTime(time) {
    if (!validTimes.has(time)) return
    state.time = time
    state.session = null
  }

  function setContext(context = {}) {
    state.context = { locationId: context.locationId || null, activity: context.activity || null }
    state.session = null
  }

  function rest() {
    state.time = nextRestTime[state.time]
    state.session = null
  }

  function dispatch(action) {
    if (action.type === 'select_npc') selectNpc(action.npcId, action.context)
    if (action.type === 'choose') choose(action.optionId)
    if (action.type === 'set_profile') setProfile(action.profile)
    if (action.type === 'set_time') setTime(action.time)
    if (action.type === 'set_context') setContext(action.context)
    if (action.type === 'rest') rest()
    if (action.type === 'leave') state.session = null
    return view()
  }

  function view() {
    const roster = npcDefinitions.map(npc => {
      const levels = unlockedLevels(npc, state)
      const dossier = (npc.dossier || []).filter(fact => matches(fact.requires, state, npc.id))
      const identityKnown = dossier.some(fact => fact.revealsIdentity)
      const relation = state.relations[npc.id] || 0
      return {
        id: npc.id,
        name: npc.name,
        role: npc.role,
        mark: npc.mark,
        displayName: identityKnown ? npc.name : '陌生人',
        displayRole: identityKnown ? npc.role : '',
        displayMark: identityKnown ? npc.mark : '·',
        identityKnown,
        relation,
        relationLabel: relation >= 2 ? '愿意深入交谈' : relation >= 1 ? '初步信任' : '尚未建立关系',
        dossier: dossier.map(({ id, label, text, source }) => ({ id, label, text, source })),
        unlocked: levels.length,
        total: npc.levels.length,
        depthLabel: levels.at(-1)?.label || '尚未认识',
        available: levels.length > 0,
        lockedHint: levels.length ? '' : npc.lockedHint,
        active: state.session?.npcId === npc.id,
      }
    })

    if (!state.session) {
      return { time: state.time, context: { ...state.context }, profile: state.profile, roster, session: null, notes: [...state.notes] }
    }

    const npc = npcs.get(state.session.npcId)
    const node = npc.nodes[state.session.nodeId]
    const blocks = visibleBlocks(node, state, npc.id)
    const options = (node.options || []).filter(option => matches(option.requires, state, npc.id))
    return {
      time: state.time,
      context: { ...state.context },
      profile: state.profile,
      roster,
      notes: [...state.notes],
      session: {
        npc: { id: npc.id, name: npc.name, role: npc.role, mark: npc.mark, description: npc.description },
        depth: state.session.depth,
        depthLabel: npc.levels.find(level => level.id === state.session.depth)?.label,
        nodeId: node.id,
        objective: node.objective || npc.objective,
        blocks,
        transcript: [...state.session.history, ...blocks],
        options,
      },
    }
  }

  return { dispatch, view }
}
