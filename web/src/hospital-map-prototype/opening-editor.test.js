import { describe, expect, test } from 'bun:test'
import { createOpeningEditor } from './opening-editor.js'

const catalog = [
  { id: 'door-single', kind: 'door', openingType: 'single-swing', leaf: 'single', spanMillimetres: 900, clearWidthMillimetres: 900, heightMillimetres: 2100, sourceKind: 'project-preset' },
  { id: 'door-double-large', kind: 'door', openingType: 'equal-double', leaf: 'double', spanMillimetres: 1800, clearWidthMillimetres: 1800, heightMillimetres: 2400, sourceKind: 'project-preset' },
  { id: 'window-exterior', kind: 'window', openingType: 'casement-window', spanMillimetres: 1800, heightMillimetres: 1500, sillHeightMillimetres: 900, sourceKind: 'project-preset' },
]
const walls = [
  { from: { x: 0, y: 0 }, to: { x: 6000, y: 0 } },
  { from: { x: 6000, y: 0 }, to: { x: 6000, y: 5000 } },
  { from: { x: 9000, y: 0 }, to: { x: 10000, y: 0 } },
]

describe('2D opening editor', () => {
  test('snaps a selected component to the nearest orthogonal wall and keeps its real dimensions', () => {
    const editor = createOpeningEditor({ catalog, walls, snapDistanceMillimetres: 750 })
    editor.selectComponent('door-single')
    const result = editor.place({ x: 2500, y: 300 })
    expect(result.change).toBe('placed')
    expect(result.placement).toMatchObject({
      componentId: 'door-single', kind: 'door', orientation: 'horizontal', center: { x: 2500, y: 0 },
      spanMillimetres: 900, clearWidthMillimetres: 900, heightMillimetres: 2100, fireRated: null, side: 1,
    })
  })

  test('rejects clicks away from walls and components wider than a wall segment', () => {
    const editor = createOpeningEditor({ catalog, walls, snapDistanceMillimetres: 750 })
    editor.selectComponent('door-single')
    expect(editor.place({ x: 2500, y: 1000 }).change).toBe('too-far')
    editor.selectComponent('door-double-large')
    expect(editor.place({ x: 9500, y: 100 }).change).toBe('no-fit')
  })

  test('prevents overlapping openings on one wall', () => {
    const editor = createOpeningEditor({ catalog, walls, snapDistanceMillimetres: 750 })
    editor.selectComponent('door-single')
    expect(editor.place({ x: 2500, y: 0 }).change).toBe('placed')
    editor.selectComponent('window-exterior')
    expect(editor.place({ x: 3000, y: 0 }).change).toBe('overlap')
  })

  test('flips a door, selects an existing opening, removes it, and serialises the layout contract', () => {
    const editor = createOpeningEditor({ catalog, walls, snapDistanceMillimetres: 750 })
    editor.selectComponent('door-single')
    const placed = editor.place({ x: 6000, y: 2500 }).placement
    expect(editor.flipSelected().placement.side).toBe(-1)
    expect(editor.select(placed.id).change).toBe('selected')
    expect(editor.removeSelected().change).toBe('removed')
    expect(JSON.parse(editor.serialise())).toEqual({
      schema: 'hospital-opening-layout/v1',
      coordinateUnit: 'millimetre',
      placements: [],
    })
  })

  test('restores a valid draft without exposing wall projection details to the caller', () => {
    const initialLayout = {
      schema: 'hospital-opening-layout/v1', coordinateUnit: 'millimetre',
      placements: [{
        id: 'opening-004', componentId: 'door-single', kind: 'door', leaf: 'single',
        wall: { from: { x: 0, y: 0 }, to: { x: 6000, y: 0 } }, wallKey: '0,0|6000,0',
        orientation: 'horizontal', center: { x: 4000, y: 0 }, spanMillimetres: 900,
        clearWidthMillimetres: 900, heightMillimetres: 2100, sillHeightMillimetres: 0, side: -1,
      }],
    }
    const editor = createOpeningEditor({ catalog, walls, snapDistanceMillimetres: 750, initialLayout })
    expect(editor.snapshot().placements).toHaveLength(1)
    editor.selectComponent('door-single')
    expect(editor.place({ x: 1000, y: 0 }).placement.id).toBe('opening-005')
  })
})
