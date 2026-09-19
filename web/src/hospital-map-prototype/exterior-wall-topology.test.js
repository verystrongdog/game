import { describe, expect, test } from 'bun:test'
import exteriorWallTopology from '../../../data/hospital_ref/floor-one-exterior-walls.json'
import { floorOneMap } from './floor-one-map.js'

const pointKey = point => `${point.x},${point.y}`
const wallKey = wall => [pointKey(wall.from), pointKey(wall.to)].sort().join('|')

function validYCoordinates(structuralGrid, x) {
  const main = structuralGrid.y.map(axis => axis.millimetres)
  const supply = structuralGrid.northSupply.y.map(axis => axis.millimetres)
  if (x < structuralGrid.northSupply.northOfXMillimetres) return new Set(supply)
  if (x === structuralGrid.northSupply.northOfXMillimetres) return new Set([...main, ...supply])
  return new Set(main)
}

describe('floor-one exterior wall topology', () => {
  test('is a closed, unbranched ring on the split structural grid', () => {
    // 来源：design/presentation/500床一层跑团地图原型.md §一·校图坐标系。
    const { structuralGrid } = floorOneMap.coordinateSystem
    const validXCoordinates = new Set(structuralGrid.x.map(axis => axis.millimetres))
    const walls = exteriorWallTopology.walls
    const wallKeys = new Set(walls.map(wallKey))
    const adjacency = new Map()

    expect(exteriorWallTopology).toMatchObject({
      schema: 'hospital-wall-topology/v1',
      coordinateUnit: 'millimetre',
    })
    expect(walls).toHaveLength(152)
    expect(wallKeys.size).toBe(walls.length)

    for (const wall of walls) {
      expect(wall.from).not.toEqual(wall.to)
      expect(wall.from.x === wall.to.x || wall.from.y === wall.to.y).toBe(true)
      for (const point of [wall.from, wall.to]) {
        expect(validXCoordinates.has(point.x)).toBe(true)
        expect(validYCoordinates(structuralGrid, point.x).has(point.y)).toBe(true)
      }

      const fromKey = pointKey(wall.from)
      const toKey = pointKey(wall.to)
      if (!adjacency.has(fromKey)) adjacency.set(fromKey, new Set())
      if (!adjacency.has(toKey)) adjacency.set(toKey, new Set())
      adjacency.get(fromKey).add(toKey)
      adjacency.get(toKey).add(fromKey)
    }

    expect([...adjacency.values()].every(neighbours => neighbours.size === 2)).toBe(true)
    const visited = new Set()
    const pending = [adjacency.keys().next().value]
    while (pending.length) {
      const current = pending.pop()
      if (visited.has(current)) continue
      visited.add(current)
      pending.push(...adjacency.get(current))
    }
    expect(visited.size).toBe(adjacency.size)
  })
})
