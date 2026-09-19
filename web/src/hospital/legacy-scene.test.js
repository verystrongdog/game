import { describe, expect, test } from 'bun:test'
import { readFileSync } from 'node:fs'

const prototypeHtml = readFileSync(
  new URL('../../../design/presentation/叙事界面原型.html', import.meta.url),
  'utf8',
)

describe('hospital prototype startup', () => {
  test('does not ship the obsolete 2D nurse-station fallback scene', () => {
    expect(prototypeHtml).not.toContain('class="hallway"')
    expect(prototypeHtml).not.toContain('class="nurse-station"')
    expect(prototypeHtml).not.toContain('class="figure"')
    expect(prototypeHtml).not.toContain('scene-hotspot')
  })

  test('keeps NPC dialogue out of the page container', () => {
    expect(prototypeHtml).not.toContain('id="dialogueRoster"')
    expect(prototypeHtml).toContain('src="/prototype-bootstrap/index.js"')
    expect(prototypeHtml).not.toContain('data-choice="good_days"')
    expect(prototypeHtml).not.toContain('感知回声')
    expect(prototypeHtml).not.toContain('赵岚')
    expect(prototypeHtml).not.toContain('登记册第三行')
  })
})
