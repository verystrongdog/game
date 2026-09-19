import { describe, expect, test } from 'bun:test'
import { floorOneMap } from './floor-one-map.js'
import {
  constrainWallPoint,
  mapPointToMillimetres,
  metricGridValues,
  millimetrePointToMap,
  snapMapPointToMillimetres,
  snapGridStepForZoom,
} from './map-coordinate.js'

// 来源：design/presentation/500床一层跑团地图原型.md §一·校图坐标系。
describe('map coordinate transforms', () => {
  test('preserves exact structural-grid coordinates', () => {
    const coordinateSystem = floorOneMap.coordinateSystem
    expect(millimetrePointToMap(coordinateSystem, { x: 82125, y: 51750 })).toEqual({ x: 78.9744, y: 27.4366 })
    expect(millimetrePointToMap(coordinateSystem, { x: -95200, y: 12000 })).toEqual({ x: 8.6339, y: 49.7435 })
  })

  test('round-trips arbitrary main-building and north-supply points to integer millimetres', () => {
    const coordinateSystem = floorOneMap.coordinateSystem
    for (const point of [{ x: 12345, y: 11111 }, { x: -70000, y: -12345 }]) {
      const position = millimetrePointToMap(coordinateSystem, point)
      expect(mapPointToMillimetres(coordinateSystem, position)).toEqual(point)
    }
  })

  test('snaps both coordinate regions to the same metric grid', () => {
    const coordinateSystem = floorOneMap.coordinateSystem
    for (const [point, expected] of [
      [{ x: 12345, y: 11111 }, { x: 12500, y: 11000 }],
      [{ x: -70120, y: -12345 }, { x: -70000, y: -12500 }],
    ]) {
      const position = millimetrePointToMap(coordinateSystem, point)
      expect(snapMapPointToMillimetres(coordinateSystem, position, 500)).toEqual(expected)
    }
    expect(metricGridValues(coordinateSystem.structuralGrid.x, 500)).toContain(0)
  })

  test('refines the snap grid with zoom and constrains wall direction', () => {
    expect([1, 2, 4, 8, 16, 32].map(snapGridStepForZoom)).toEqual([1000, 500, 250, 100, 50, 25])
    const anchor = { x: 1000, y: 2000 }
    const point = { x: 3500, y: 4500 }
    expect(constrainWallPoint(anchor, point, 'horizontal')).toEqual({ x: 3500, y: 2000 })
    expect(constrainWallPoint(anchor, point, 'vertical')).toEqual({ x: 1000, y: 4500 })
  })
})
