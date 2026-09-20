import { describe, expect, test } from 'bun:test'
import { createDialogueRuntime } from '../dialogue/dialogue-runtime.js'
import { npcDialogues } from '../dialogue/npcs/index.js'
import { floorOneMap } from './floor-one-map.js'
import { createFloorMapRuntime } from './floor-map-runtime.js'

describe('floor map runtime', () => {
  test('exposes only adjacent destinations as reachable', () => {
    const runtime = createFloorMapRuntime(floorOneMap)
    const view = runtime.view()
    expect(view.currentLocation.id).toBe('entrance')
    expect(view.locations.find(location => location.id === 'outpatient').reachable).toBe(true)
    expect(view.locations.find(location => location.id === 'nurse_station').reachable).toBe(false)
  })

  test('rejects jumps and moves along a declared connection', () => {
    const runtime = createFloorMapRuntime(floorOneMap)
    expect(runtime.move('nurse_station')).toMatchObject({ moved: false, reason: 'not-adjacent' })
    expect(runtime.move('outpatient')).toMatchObject({ moved: true, currentLocation: { id: 'outpatient' } })
  })

  test('derives actor co-location from the current position', () => {
    const runtime = createFloorMapRuntime(floorOneMap, 'nurse_station')
    expect(runtime.view().actors.filter(actor => actor.coLocated).map(actor => actor.id)).toEqual([
      'zheng_xiaomin',
      'tan_lijuan',
    ])
  })

  test('moves or removes actors according to the canonical three time periods', () => {
    // 来源：design/presentation/开局剧情逻辑原型.md §3.4。
    const runtime = createFloorMapRuntime(floorOneMap, 'activity_room')
    const afternoon = runtime.view('afternoon')
    expect(afternoon.actors.find(actor => actor.id === 'zhou_weiguo')).toMatchObject({ location: 'activity_room', activity: '修轮椅刹车', coLocated: true })
    expect(afternoon.actors.some(actor => actor.id === 'tan_lijuan')).toBe(false)
  })

  test('reaches the afternoon basketball-court actor through the canonical rest action', () => {
    // 来源：design/events/游戏循环.md §2.2；design/events/剧情系统设计.md §3.8.2。
    const map = createFloorMapRuntime(floorOneMap, 'basketball_court')
    const dialogue = createDialogueRuntime({ npcDefinitions: npcDialogues })
    expect(map.view(dialogue.view().time).actors.filter(actor => actor.coLocated)).toEqual([])

    dialogue.dispatch({ type: 'rest' })
    expect(dialogue.view().time).toBe('afternoon')
    expect(map.view(dialogue.view().time).actors.filter(actor => actor.coLocated).map(actor => actor.id)).toContain('wu_tong')
  })

  test('provides sight, sound, and smell at every location and time', () => {
    // 来源：design/presentation/开局剧情逻辑原型.md §3.5。
    for (const location of floorOneMap.locations) {
      for (const time of ['morning', 'afternoon', 'night']) {
        expect(location.atmosphere[time]).toEqual({
          sight: expect.any(String), sound: expect.any(String), smell: expect.any(String),
        })
      }
    }
  })
})
