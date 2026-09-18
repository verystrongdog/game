import { describe, expect, test } from 'bun:test'
import { clampBrightness } from './display-settings.js'

describe('display brightness', () => {
  test('keeps the setting inside the authored presentation range', () => {
    expect(clampBrightness(40)).toBe(70)
    expect(clampBrightness(115)).toBe(115)
    expect(clampBrightness(180)).toBe(140)
    expect(clampBrightness('invalid')).toBe(100)
  })
})
