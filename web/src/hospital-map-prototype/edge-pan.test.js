import { describe, expect, test } from 'bun:test'
import { EDGE_PAN_MAX_SPEED, edgePanVelocity } from './edge-pan.js'

describe('map edge pan', () => {
  test('accelerates toward either viewport edge and stops in the centre', () => {
    // 来源：design/presentation/500床一层跑团地图原型.md §一·校图坐标系。
    expect(edgePanVelocity(0, 0, 1000)).toBe(-EDGE_PAN_MAX_SPEED)
    expect(edgePanVelocity(24, 0, 1000)).toBe(-EDGE_PAN_MAX_SPEED / 2)
    expect(edgePanVelocity(500, 0, 1000)).toBe(0)
    expect(edgePanVelocity(976, 0, 1000)).toBe(EDGE_PAN_MAX_SPEED / 2)
    expect(edgePanVelocity(1000, 0, 1000)).toBe(EDGE_PAN_MAX_SPEED)
  })

  test('does not pan for a pointer outside the viewport', () => {
    expect(edgePanVelocity(-1, 0, 1000)).toBe(0)
    expect(edgePanVelocity(1001, 0, 1000)).toBe(0)
  })
})
