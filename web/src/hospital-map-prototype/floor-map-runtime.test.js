import { describe, expect, test } from 'bun:test'
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
})
