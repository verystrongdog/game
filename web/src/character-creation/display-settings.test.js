import { describe, expect, test } from 'bun:test'
import { readFileSync } from 'node:fs'
import { clampBrightness } from './display-settings.js'

const css = readFileSync(new URL('./character-creation.css', import.meta.url), 'utf8')

describe('display brightness', () => {
  test('keeps the setting inside the authored presentation range', () => {
    expect(clampBrightness(40)).toBe(70)
    expect(clampBrightness(115)).toBe(115)
    expect(clampBrightness(180)).toBe(140)
    expect(clampBrightness('invalid')).toBe(100)
  })

  test('adjusts brightness without filtering and rerasterizing the map', () => {
    expect(css).not.toMatch(/filter:\s*brightness/)
    expect(css).toContain('.display-brightness-adjusted body::before')
    expect(css).toContain('.display-brightness-adjusted body::after')
  })
})
