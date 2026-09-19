import { describe, expect, test } from 'bun:test'
import { MAX_ZOOM, nextWheelZoom, wheelZoomTarget } from './zoom-motion.js'

describe('map wheel zoom motion', () => {
  test('uses wheel magnitude so faster input travels farther', () => {
    const start = 1.35
    const slow = wheelZoomTarget(start, -10)
    const fast = wheelZoomTarget(start, -100)
    expect(slow).toBeGreaterThan(start)
    expect(fast).toBeGreaterThan(slow)
    expect(fast - start).toBeGreaterThan((slow - start) * 5)
  })

  test('approaches the target over multiple frames without overshooting', () => {
    const target = wheelZoomTarget(1.35, -100)
    const firstFrame = nextWheelZoom(1.35, target)
    const secondFrame = nextWheelZoom(firstFrame, target)
    expect(firstFrame).toBeGreaterThan(1.35)
    expect(firstFrame).toBeLessThan(target)
    expect(secondFrame).toBeGreaterThan(firstFrame)
    expect(secondFrame).toBeLessThan(target)
  })

  test('allows high-detail wall drafting zoom', () => {
    // 来源：design/presentation/500床一层跑团地图原型.md §四。
    expect(MAX_ZOOM).toBe(64)
  })
})
