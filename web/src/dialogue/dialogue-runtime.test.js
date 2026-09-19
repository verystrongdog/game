import { describe, expect, test } from 'bun:test'
import { createDialogueRuntime } from './dialogue-runtime.js'
import { npcDialogues } from './npcs/index.js'
import { dialogueProfilePresets } from './profile-presets.js'

const createRuntime = () => createDialogueRuntime({ npcDefinitions: npcDialogues })
const npc = (view, id) => view.roster.find(item => item.id === id)

describe('NPC-owned dialogue runtime', () => {
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
    expect(runtime.view().session.options.map(option => option.id)).toContain('ocd_answer')
    expect(runtime.view().session.blocks.some(block => block.kind === 'disease')).toBe(true)
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
