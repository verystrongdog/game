import { describe, expect, test } from 'bun:test'
import { createDialogueRuntime } from './dialogue-runtime.js'
import { npcDialogues } from './npcs/index.js'
import { dialogueProfilePresets } from './profile-presets.js'

const createRuntime = () => createDialogueRuntime({ npcDefinitions: npcDialogues })
const npc = (view, id) => view.roster.find(item => item.id === id)

describe('NPC-owned dialogue runtime', () => {
  test('keeps the second dialogue-volume pass substantial and NPC-owned', () => {
    // 来源：design/presentation/开局剧情逻辑原型.md §3.4。
    for (const definition of npcDialogues) {
      expect(Object.keys(definition.nodes).length).toBeGreaterThanOrEqual(12)
      const surfaceEntry = definition.levels[0].entry || definition.levels[0].entries.at(-1).node
      expect(definition.nodes[surfaceEntry].options.length).toBeGreaterThanOrEqual(3)
      for (const node of Object.values(definition.nodes)) {
        for (const option of node.options || []) {
          if (option.next) expect(definition.nodes[option.next]).toBeDefined()
        }
      }
    }
  })

  test('keeps patient first meetings on observable behaviour instead of diagnosis or trauma disclosure', () => {
    // 来源：design/presentation/开局剧情逻辑原型.md §3.4。
    for (const id of ['wu_tong', 'zhou_weiguo', 'tang_nianan']) {
      const definition = npcDialogues.find(item => item.id === id)
      const node = definition.nodes[definition.levels[0].entry]
      const firstMeetingText = [...node.blocks.map(block => block.text), ...node.options.map(option => option.text)].join('')
      expect(firstMeetingText).not.toMatch(/为什么住院|我有病|心电图|伤害女儿|受过什么创伤/)
    }
  })

  test('omits unknown dossier fields and reveals identity through conversation or records', () => {
    const runtime = createRuntime()
    expect(npc(runtime.view(), 'wu_tong')).toMatchObject({ displayName: '陌生人', dossier: [] })

    runtime.dispatch({ type: 'select_npc', npcId: 'wu_tong' })
    expect(npc(runtime.view(), 'wu_tong').displayName).toBe('吴桐')
    expect(npc(runtime.view(), 'wu_tong').dossier.map(fact => fact.label)).toEqual(['身份', '当面观察'])

    const recordRuntime = createRuntime()
    recordRuntime.dispatch({ type: 'select_npc', npcId: 'zheng_xiaomin' })
    recordRuntime.dispatch({ type: 'choose', optionId: 'handover' })
    expect(npc(recordRuntime.view(), 'tan_lijuan').displayName).toBe('谭丽娟')
    expect(npc(recordRuntime.view(), 'tan_lijuan').dossier.map(fact => fact.label)).toContain('交接本记录')
  })

  test('reveals authored dossier facts only after their dialogue and relation gates', () => {
    const runtime = createRuntime()
    runtime.dispatch({ type: 'select_npc', npcId: 'wu_tong' })
    expect(npc(runtime.view(), 'wu_tong').dossier.map(fact => fact.label)).not.toContain('她的说法')
    runtime.dispatch({ type: 'choose', optionId: 'numbers' })
    expect(npc(runtime.view(), 'wu_tong').dossier.map(fact => fact.label)).toContain('她的说法')
  })

  test('unlocks people and dialogue depth only after their trigger conditions', () => {
    const runtime = createRuntime()
    expect(npc(runtime.view(), 'tan_lijuan').available).toBe(false)

    runtime.dispatch({ type: 'select_npc', npcId: 'zheng_xiaomin' })
    runtime.dispatch({ type: 'choose', optionId: 'handover' })
    runtime.dispatch({ type: 'choose', optionId: 'leave' })
    expect(npc(runtime.view(), 'tan_lijuan').available).toBe(true)
    expect(npc(runtime.view(), 'zheng_xiaomin').unlocked).toBe(1)

    runtime.dispatch({ type: 'select_npc', npcId: 'zheng_xiaomin' })
    runtime.dispatch({ type: 'choose', optionId: 'good_days' })
    runtime.dispatch({ type: 'choose', optionId: 'leave' })
    expect(npc(runtime.view(), 'zheng_xiaomin').depthLabel).toBe('熟悉')
  })

  test('filters experience and disease presentation through the active profile', () => {
    const runtime = createRuntime()
    runtime.dispatch({ type: 'select_npc', npcId: 'zheng_xiaomin' })
    expect(runtime.view().session.blocks.map(block => block.kind)).toEqual(['description', 'npc'])

    runtime.dispatch({ type: 'set_profile', profile: dialogueProfilePresets.find(profile => profile.id === 'night_watch') })
    runtime.dispatch({ type: 'select_npc', npcId: 'zheng_xiaomin' })
    expect(runtime.view().session.blocks.map(block => block.kind)).toEqual(['description', 'npc', 'experience', 'disease'])
  })

  test('lets a disease open an authored response instead of adding generic perception text', () => {
    const runtime = createRuntime()
    runtime.dispatch({ type: 'set_profile', profile: dialogueProfilePresets.find(profile => profile.id === 'checker') })
    runtime.dispatch({ type: 'select_npc', npcId: 'tang_nianan' })
    runtime.dispatch({ type: 'choose', optionId: 'phone' })
    runtime.dispatch({ type: 'choose', optionId: 'leave' })
    runtime.dispatch({ type: 'select_npc', npcId: 'tang_nianan' })
    expect(runtime.view().session.options.map(option => option.id)).toContain('ocd_answer')
    expect(runtime.view().session.blocks.some(block => block.kind === 'disease')).toBe(true)
  })

  test('selects dialogue from the NPC current location, time, and activity', () => {
    const runtime = createRuntime()
    runtime.dispatch({ type: 'set_time', time: 'afternoon' })
    runtime.dispatch({
      type: 'select_npc',
      npcId: 'wu_tong',
      context: { locationId: 'basketball_court', activity: '沿边线计步' },
    })
    expect(runtime.view().session.nodeId).toBe('wu_court')

    runtime.dispatch({ type: 'set_time', time: 'morning' })
    runtime.dispatch({
      type: 'select_npc',
      npcId: 'wu_tong',
      context: { locationId: 'north_ward', activity: '整理称重记录' },
    })
    expect(runtime.view().session.nodeId).toBe('wu_surface')
  })

  test('keeps conversations open so the player can return from replies to their topic hubs', () => {
    // 来源：design/events/剧情系统设计.md §3.3；design/presentation/开局剧情逻辑原型.md §3.4。
    const paths = [
      { npcId: 'wu_tong', optionId: 'numbers', reply: 'wu_numbers', hub: 'wu_surface' },
      { npcId: 'zhou_weiguo', optionId: 'work', reply: 'zhou_work', hub: 'zhou_surface' },
      { npcId: 'tang_nianan', optionId: 'photo', reply: 'tang_photo', hub: 'tang_surface' },
    ]

    for (const path of paths) {
      const runtime = createRuntime()
      runtime.dispatch({ type: 'select_npc', npcId: path.npcId })
      runtime.dispatch({ type: 'choose', optionId: path.optionId })
      expect(runtime.view().session.nodeId).toBe(path.reply)
      expect(runtime.view().session.options.map(option => option.id)).toContain('back')

      runtime.dispatch({ type: 'choose', optionId: 'back' })
      expect(runtime.view().session.nodeId).toBe(path.hub)
    }
  })

  test('does not let a surface situation hide newly unlocked relationship dialogue', () => {
    // 来源：design/events/剧情系统设计.md §3.3、§3.8.1。
    const runtime = createRuntime()
    runtime.dispatch({ type: 'set_time', time: 'afternoon' })
    const context = { locationId: 'activity_room', activity: '修轮椅刹车' }
    runtime.dispatch({ type: 'select_npc', npcId: 'zhou_weiguo', context })
    expect(runtime.view().session.nodeId).toBe('zhou_activity_room')

    runtime.dispatch({ type: 'choose', optionId: 'hold' })
    expect(npc(runtime.view(), 'zhou_weiguo').depthLabel).toBe('熟悉')

    runtime.dispatch({ type: 'select_npc', npcId: 'zhou_weiguo', context })
    expect(runtime.view().session.nodeId).toBe('zhou_familiar')
  })

  test('appends dialogue beats and the chosen player action to one continuous session transcript', () => {
    // 来源：design/events/剧情系统设计.md §3.8.2。
    const runtime = createRuntime()
    runtime.dispatch({ type: 'set_time', time: 'afternoon' })
    const context = { locationId: 'basketball_court', activity: '沿边线计步' }
    runtime.dispatch({ type: 'select_npc', npcId: 'wu_tong', context })
    const opening = runtime.view().session.blocks

    runtime.dispatch({ type: 'choose', optionId: 'count' })
    const session = runtime.view().session
    expect(session.nodeId).toBe('wu_court_count')
    expect(session.transcript.slice(0, opening.length)).toEqual(opening)
    expect(session.transcript[opening.length]).toMatchObject({ kind: 'player', speaker: '你' })
    expect(session.transcript.at(-1).speaker).toBe('吴桐')
  })

  test('offers speech, action, observation, and silence as different ways into the court scene', () => {
    // 来源：design/events/剧情系统设计.md §3.8.2。
    const runtime = createRuntime()
    runtime.dispatch({ type: 'set_time', time: 'afternoon' })
    runtime.dispatch({
      type: 'select_npc',
      npcId: 'wu_tong',
      context: { locationId: 'basketball_court', activity: '沿边线计步' },
    })

    expect(runtime.view().session.options.map(option => option.id)).toEqual(['count', 'parallel', 'foot', 'wait'])
  })

  test('reveals experience observations inside a concrete situation', () => {
    const runtime = createRuntime()
    runtime.dispatch({ type: 'set_profile', profile: { id: 'hunger', label: '饥饿经历', experiences: ['hunger'], diseases: [] } })
    runtime.dispatch({ type: 'set_time', time: 'afternoon' })
    runtime.dispatch({
      type: 'select_npc',
      npcId: 'wu_tong',
      context: { locationId: 'basketball_court', activity: '沿边线计步' },
    })
    expect(runtime.view().session.blocks).toContainEqual(expect.objectContaining({ kind: 'experience', source: '经历 · 长期挨过饿' }))
  })

  test('supports the canonical three time periods for presentation previews', () => {
    const runtime = createRuntime()
    for (const time of ['morning', 'afternoon', 'night']) {
      runtime.dispatch({ type: 'set_time', time })
      expect(runtime.view().time).toBe(time)
    }
    runtime.dispatch({ type: 'set_time', time: 'midnight' })
    expect(runtime.view().time).toBe('night')
  })
})
