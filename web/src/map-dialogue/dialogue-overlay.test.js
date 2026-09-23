import { describe, expect, test } from 'bun:test'
import { readFileSync } from 'node:fs'

const source = readFileSync(new URL('./dialogue-overlay.js', import.meta.url), 'utf8')
const css = readFileSync(new URL('./dialogue-overlay.css', import.meta.url), 'utf8')
const bootstrap = readFileSync(new URL('../prototype-bootstrap/index.js', import.meta.url), 'utf8')
const dialogueUi = readFileSync(new URL('../dialogue/dialogue-ui.js', import.meta.url), 'utf8')
const prototypeHtml = readFileSync(new URL('../../../design/presentation/叙事界面原型.html', import.meta.url), 'utf8')

describe('map dialogue overlay', () => {
  test('drives the shared dialogue runtime instead of keeping its own session', () => {
    // 来源：design/presentation/500床一层跑团地图原型.md §2.4。
    expect(source).toContain('dialogue.selectNpc(npcId, { nearby: true')
    expect(source).toContain('dialogue.choose(')
    expect(source).toContain('dialogue.leave()')
    expect(source).toContain('dialogue.subscribe(() => render())')
    // 浮层不得自己求值条件或自己算效果：那属于 dialogue-runtime。
    expect(source).not.toContain('requires')
    expect(source).not.toContain('relationDelta')
    expect(source).not.toContain('flagsAdd')
  })

  test('opens and closes without dropping the shared session state', () => {
    expect(source).toContain("element.hidden = false")
    expect(source).toContain('if (element.hidden) return')
    expect(source).toContain('dialogue.subscribe')
    expect(css).toContain('.md-overlay[hidden] { display: none; }')
    expect(source).toContain("event.key === 'Escape'")
  })

  test('keeps the continuous transcript readable after the session ends', () => {
    // 来源：design/presentation/场景化对话与任务写作方法.md §八（连续记录，不清空前文）。
    expect(source).toContain('closing')
    expect(source).toContain('transcript: [...before.transcript')
    expect(source).toContain('这次谈话到此为止')
  })

  test('scrolls a bounded transcript region and reuses opening-exploration block language', () => {
    expect(css).toMatch(/\.md-transcript\s*\{[^}]*min-height:\s*0[^}]*overflow-y:\s*auto/)
    expect(css).toMatch(/\.md-narrative\s*\{[^}]*grid-template-rows:\s*auto minmax\(0,1fr\) auto/)
    expect(css).toContain('.md-beat.experience')
    expect(css).toContain('.md-beat.disease')
    expect(css).toContain('.md-beat.player')
    expect(css).toContain('.md-beat.evidence')
  })

  test('stays a modal that keeps the rest of the prototype out of the way', () => {
    expect(source).toContain("element.setAttribute('role', 'dialog')")
    expect(source).toContain("element.setAttribute('aria-modal', 'true')")
    expect(source).toContain('stopImmediatePropagation')
    expect(css).toContain('.md-open { overflow: hidden !important; }')
  })

  test('writes the registered distance exception on the interface itself', () => {
    // 来源：design/presentation/叙事界面布局.md §四·8 的 2026-09-23 临时例外。
    expect(source).toContain('md-prototype-note')
    expect(source).toContain('还没有玩家坐标')
    expect(css).toContain('.md-prototype-note')
  })

  test('is wired into the prototype bootstrap and the served page', () => {
    expect(prototypeHtml).toContain('/map-dialogue/dialogue-overlay.css')
    expect(bootstrap).toContain("import { createDialogueOverlay } from '/map-dialogue/dialogue-overlay.js'")
    expect(bootstrap).toContain('createDialogueOverlay({ dialogue: dialoguePrototype })')
    expect(bootstrap).toContain('onNpcSelect: (npcId, context) => dialogueOverlay.open(npcId, context)')
    expect(dialogueUi).toContain('choose(optionId) {')
    expect(dialogueUi).toContain('leave() {')
  })
})
