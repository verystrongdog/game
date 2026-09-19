import { describe, expect, test } from 'bun:test'
import { createWallTrace, serialiseWallTopology } from './wall-trace.js'

// 来源：design/presentation/500床一层跑团地图原型.md §一·校图坐标系（总体轴网整数毫米坐标）。
const a = { x: 0, y: 0 }
const b = { x: 7500, y: 0 }
const c = { x: 7500, y: -6900 }

describe('wall trace', () => {
  test('builds a continuous wall chain from successive grid intersections', () => {
    const trace = createWallTrace()
    expect(trace.select(a).change).toBe('started')
    expect(trace.select(b).topology).toMatchObject({
      activeAnchor: b,
      walls: [{ from: a, to: b }],
    })
    expect(trace.select(c).topology.walls).toEqual([
      { from: a, to: b },
      { from: b, to: c },
    ])
  })

  test('finishes on the active point without creating a zero-length wall', () => {
    const trace = createWallTrace()
    trace.select(a)
    expect(trace.select(a)).toMatchObject({ change: 'finished', topology: { activeAnchor: null, walls: [] } })
  })

  test('deduplicates a wall regardless of endpoint order', () => {
    const trace = createWallTrace()
    trace.select(a)
    trace.select(b)
    trace.finish()
    trace.select(b)
    expect(trace.select(a)).toMatchObject({ change: 'duplicate', topology: { walls: [{ from: a, to: b }] } })
  })

  test('undo removes the last segment and resumes at its starting point', () => {
    const trace = createWallTrace()
    trace.select(a)
    trace.select(b)
    trace.select(c)
    expect(trace.undo()).toMatchObject({
      change: 'undone',
      topology: { activeAnchor: b, walls: [{ from: a, to: b }] },
    })
  })

  test('serialises only completed millimetre wall segments', () => {
    const trace = createWallTrace()
    trace.select(a)
    trace.select(b)
    const output = JSON.parse(serialiseWallTopology(trace.snapshot()))
    expect(output).toEqual({
      schema: 'hospital-wall-topology/v1',
      coordinateUnit: 'millimetre',
      walls: [{ from: a, to: b }],
    })
    expect(output).not.toHaveProperty('activeAnchor')
  })

  test('loads initial walls as an immutable editing baseline', () => {
    const initialFrom = { x: 0, y: 0 }
    const initialTo = { x: 7500, y: 0 }
    const initial = {
      schema: 'hospital-wall-topology/v1',
      coordinateUnit: 'millimetre',
      walls: [{ from: initialFrom, to: initialTo }],
    }
    const trace = createWallTrace(initial)

    initial.walls[0].from.x = 123
    expect(trace.snapshot().walls).toEqual([{ from: { x: 0, y: 0 }, to: initialTo }])
    expect(trace.undo().change).toBe('unchanged')

    trace.select(initialTo)
    trace.select(c)
    expect(trace.clear()).toMatchObject({
      change: 'cleared',
      topology: { activeAnchor: null, walls: [{ from: { x: 0, y: 0 }, to: initialTo }] },
    })
  })

  test('rejects malformed initial topology', () => {
    expect(() => createWallTrace({ schema: 'other', coordinateUnit: 'millimetre', walls: [] })).toThrow()
    expect(() => createWallTrace({
      schema: 'hospital-wall-topology/v1',
      coordinateUnit: 'millimetre',
      walls: [{ from: a, to: a }],
    })).toThrow()
  })
})
