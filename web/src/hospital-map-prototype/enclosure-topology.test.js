import { describe, expect, test } from 'bun:test'
import { calculateEnclosureTopology } from './enclosure-topology.js'

const topology = walls => ({ schema: 'hospital-wall-topology/v1', coordinateUnit: 'millimetre', walls })
const wall = (x1, y1, x2, y2) => ({ from: { x: x1, y: y1 }, to: { x: x2, y: y2 } })

describe('hospital enclosure topology', () => {
  test('finds one bounded enclosure and verifies it through Euler topology', () => {
    const result = calculateEnclosureTopology([topology([
      wall(0, 0, 4000, 0), wall(4000, 0, 4000, 3000),
      wall(4000, 3000, 0, 3000), wall(0, 3000, 0, 0),
    ])])
    expect(result).toMatchObject({ sourceWallCount: 4, planarEdgeCount: 4, vertexCount: 4, connectedComponentCount: 1 })
    expect(result.planarWalls).toHaveLength(4)
    expect(result.enclosures).toHaveLength(1)
    expect(result.enclosures[0].areaSquareMillimetres).toBe(12_000_000)
    expect(result.diagnostics.degreeOneEndpoints).toEqual([])
  })

  test('splits crossing partitions and deduplicates repeated source exports', () => {
    const outer = [
      wall(0, 0, 4000, 0), wall(4000, 0, 4000, 3000),
      wall(4000, 3000, 0, 3000), wall(0, 3000, 0, 0),
    ]
    const result = calculateEnclosureTopology([
      topology(outer),
      topology([...outer, wall(2000, 0, 2000, 3000), wall(0, 1500, 4000, 1500)]),
    ])
    expect(result.sourceWallCount).toBe(6)
    expect(result.enclosures).toHaveLength(4)
    expect(result.enclosures.every(item => item.areaSquareMillimetres === 3_000_000)).toBe(true)
  })

  test('reports a degree-one endpoint without classifying or welding it', () => {
    const result = calculateEnclosureTopology([topology([
      wall(0, 0, 4000, 0), wall(4000, 0, 4000, 3000),
      wall(4000, 3000, 0, 3000), wall(0, 3000, 0, 0),
      wall(2000, 25, 2000, 1500),
    ])])
    expect(result.enclosures).toHaveLength(1)
    expect(result.diagnostics.degreeOneEndpoints).toContainEqual({ x: 2000, y: 25 })
    expect(result.diagnostics.degreeOneEndpoints).toContainEqual({ x: 2000, y: 1500 })
  })
})
