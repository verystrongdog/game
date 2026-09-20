import { describe, expect, test } from 'bun:test'
import { readFileSync } from 'node:fs'

const html = readFileSync(new URL('../../../design/presentation/叙事界面原型.html', import.meta.url), 'utf8')
const bootstrap = readFileSync(new URL('./index.js', import.meta.url), 'utf8')
const characterCreation = readFileSync(new URL('../character-creation/index.js', import.meta.url), 'utf8')
const dialogueUi = readFileSync(new URL('../dialogue/dialogue-ui.js', import.meta.url), 'utf8')
const placementEditor = readFileSync(new URL('../hospital/placement-editor.js', import.meta.url), 'utf8')
const openingCss = readFileSync(new URL('../opening-exploration/opening.css', import.meta.url), 'utf8')

describe('narrative prototype shell', () => {
  test('gates mandatory character creation behind the new-game screen', () => {
    expect(html).toContain('id="startScreen"')
    expect(html).toContain('id="startGameButton"')
    expect(bootstrap).toContain('required: true')
    expect(bootstrap).toMatch(/startGameButton\.addEventListener\('click',[\s\S]*characterCreation\.open\(\)/)
    expect(characterCreation).toContain('data-confirm')
    expect(characterCreation).toContain('if (required && !state.completed)')
  })

  test('offers a development-only default character shortcut', () => {
    expect(characterCreation).toContain('import.meta.env.DEV')
    expect(characterCreation).toContain('data-dev-default')
    expect(characterCreation).toContain('developmentDefaultCharacter')
  })

  test('keeps prototype controls inside the developer panel', () => {
    const developerPanel = html.match(/<section class="developer-options"[\s\S]*?<\/section>\s*<\/section>\s*<\/section>/)?.[0] || ''
    expect(developerPanel).toContain('id="mapViewButton"')
    expect(developerPanel).toContain('id="characterCreationLaunch"')
    expect(developerPanel).toContain('data-dev-map="rotate-left"')
    expect(developerPanel).toContain('data-dev-wall="copy"')
    expect(developerPanel).toContain('data-dev-wall-mode="opening"')
    expect(developerPanel).toContain('data-dev-opening-component="door-single"')
    expect(developerPanel).toContain('data-dev-opening="copy"')
    expect(developerPanel).toContain('data-dev-time="afternoon"')
  })

  test('applies the dialogue time to the scene presentation layer', () => {
    expect(bootstrap).toContain('scene.dataset.time = view.time')
    expect(html).toContain('.scene[data-time="afternoon"]')
    expect(html).toContain('.scene[data-time="night"]')
  })

  test('exposes canonical rest outside the developer-only time controls', () => {
    // 来源：design/events/游戏循环.md §2.2；design/presentation/开局剧情逻辑原型.md §3.3。
    expect(dialogueUi).toContain('data-dialogue-rest')
    expect(dialogueUi).toContain("runtime.dispatch({ type: 'rest' })")
  })

  test('does not expose remote NPC conversation cards', () => {
    expect(html).not.toContain('id="dialogueRoster"')
    expect(dialogueUi).not.toContain('data-dialogue-npc')
    expect(dialogueUi).toContain('if (!nearby) return runtime.view()')
  })

  test('hosts the hospital placement toggle in developer options', () => {
    expect(html).toContain('id="hospitalPlacementLaunch"')
    expect(html).toContain("toggleButton: document.querySelector('#hospitalPlacementLaunch')")
    expect(placementEditor).toContain('const toggle = toggleButton || document.createElement')
  })

  test('keeps overflowing opening dialogue inside a bounded scroll region', () => {
    // 来源：design/presentation/主角开场场景示范.md §2.2；连续叙事记录必须可回滚。
    expect(openingCss).toMatch(/\.oe-narrative\s*\{[^}]*min-height:\s*0/)
    expect(openingCss).toMatch(/\.oe-transcript\s*\{[^}]*overflow-y:\s*auto/)
  })
})
