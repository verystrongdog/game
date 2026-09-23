import { describe, expect, test } from 'bun:test'
import { readFileSync } from 'node:fs'
import {
  ROOM_DESCRIPTION_STATUS,
  createRoomDescriptionIndex,
  describeRoom,
  measureEnclosure,
  roomCategories,
  roomCategoryOf,
} from './room-description.js'

// 来源：design/presentation/500床一层跑团地图原型.md §2.2（owner 2026-09-23：只按几何分类，不命名不落正典）。
const topology = JSON.parse(readFileSync(new URL('../../../data/hospital_ref/floor-one-enclosures.json', import.meta.url), 'utf8'))

const rectangle = (widthMillimetres, heightMillimetres, id = 'test') => ({
  id,
  areaSquareMillimetres: widthMillimetres * heightMillimetres,
  boundary: [
    { x: 0, y: 0 },
    { x: widthMillimetres, y: 0 },
    { x: widthMillimetres, y: heightMillimetres },
    { x: 0, y: heightMillimetres },
  ],
})

describe('geometry-derived room descriptions', () => {
  test('never names rooms or claims a use', () => {
    expect(ROOM_DESCRIPTION_STATUS).toBe('geometry-derived-placeholder-not-canon')
    const forbidden = ['病房', '护士站', '药房', '活动室', '诊室', '值班室', '庭院', '病区']
    const texts = []
    for (const category of roomCategories) {
      expect(forbidden.some(term => category.label.includes(term))).toBe(false)
      for (const variant of category.variants) {
        texts.push(variant(measureEnclosure(rectangle(6_900, 6_900))))
        texts.push(variant(measureEnclosure(rectangle(48_300, 3_000))))
      }
    }
    expect(texts.length).toBeGreaterThan(20)
    for (const term of forbidden) expect(texts.join('\n')).not.toContain(term)
  })

  test('classifies by measured geometry alone', () => {
    // 形状（长宽比）先于尺度（面积）：144.9 m² 的 3.0×48.3 m 长条是走道，不是大跨空间。
    expect(roomCategoryOf(measureEnclosure(rectangle(48_300, 3_000))).id).toBe('corridor')
    expect(roomCategoryOf(measureEnclosure(rectangle(20_000, 5_000))).id).toBe('open-hall')
    expect(roomCategoryOf(measureEnclosure(rectangle(12_600, 4_000))).id).toBe('passage')
    expect(roomCategoryOf(measureEnclosure(rectangle(6_900, 6_900))).id).toBe('standard-room')
    expect(roomCategoryOf(measureEnclosure(rectangle(6_000, 4_000))).id).toBe('room')
    expect(roomCategoryOf(measureEnclosure(rectangle(4_000, 3_000))).id).toBe('small-room')
    expect(roomCategoryOf(measureEnclosure(rectangle(2_000, 2_000))).id).toBe('shaft')
  })

  test('gives every floor-one enclosure a category, a description, and its measurements', () => {
    const index = createRoomDescriptionIndex(topology.enclosures)
    expect(index.size).toBe(189)
    const categories = new Set()
    for (const enclosure of topology.enclosures) {
      const described = index.get(enclosure.id)
      expect(described.enclosureId).toBe(enclosure.id)
      expect(described.status).toBe(ROOM_DESCRIPTION_STATUS)
      expect(described.description.length).toBeGreaterThan(30)
      expect(described.facts).toHaveLength(5)
      expect(described.facts[0]).toContain('面积')
      expect(described.unknown).toContain('名称')
      categories.add(described.categoryId)
    }
    // 一层同时存在大跨空间、长走道、房间模块与极小围合；分类不是单一兜底。
    expect([...categories].sort()).toEqual([
      'corridor', 'open-hall', 'passage', 'room', 'shaft', 'small-room', 'standard-room',
    ])
  })

  test('matches the category readings published in the design document', () => {
    // 同一事实只有一个权威来源：设计文档 §2.2 写下的读数必须等于代码算出来的读数。
    const counts = {}
    for (const enclosure of topology.enclosures) {
      const { categoryId } = describeRoom(enclosure)
      counts[categoryId] = (counts[categoryId] || 0) + 1
    }
    expect(counts).toEqual({
      corridor: 6,
      'open-hall': 11,
      passage: 7,
      'standard-room': 58,
      room: 80,
      'small-room': 25,
      shaft: 2,
    })
  })

  test('states measured facts instead of rounded adjectives', () => {
    const described = describeRoom({ ...rectangle(6_900, 6_900, 'f1-enclosure-fixture'), areaSquareMillimetres: 47_610_000 })
    expect(described.areaText).toBe('47.6 m²')
    expect(described.shapeText).toBe('6.9 × 6.9 m')
    expect(described.facts).toContain('面积 47.6 m²')
    expect(described.facts).toContain('短边 6.9 m · 长边 6.9 m · 长宽比 1 比 1')
    expect(described.facts).toContain('边界 4 个顶点')
    expect(described.description).toContain('6.9 米')
    expect(described.basis).toContain('floor-one-enclosures.json')
  })

  test('picks the same sentence variant for the same enclosure id', () => {
    const first = describeRoom(rectangle(6_900, 6_900, 'f1-enclosure-979419c9'))
    const second = describeRoom(rectangle(6_900, 6_900, 'f1-enclosure-979419c9'))
    expect(first).toEqual(second)
    const variants = new Set(topology.enclosures
      .filter(enclosure => enclosure.areaSquareMillimetres >= 40_000_000 && enclosure.areaSquareMillimetres < 60_000_000)
      .map(enclosure => describeRoom(enclosure).description))
    expect(variants.size).toBeGreaterThan(1)
  })

  test('derives orientation wording from the documented plan-north convention', () => {
    // 来源：上文 §一·校图坐标系（指北针朝图面左侧 ⇒ +X 向南、+Y 向东）。
    const mainBuilding = describeRoom({ id: 'main', areaSquareMillimetres: 47_610_000, boundary: [
      { x: 1000, y: 1000 }, { x: 7900, y: 1000 }, { x: 7900, y: 7900 }, { x: 1000, y: 7900 },
    ] })
    const supplyCentre = describeRoom({ id: 'supply', areaSquareMillimetres: 47_610_000, boundary: [
      { x: -90_000, y: 1000 }, { x: -83_100, y: 1000 }, { x: -83_100, y: 7900 }, { x: -90_000, y: 7900 },
    ] })
    expect(mainBuilding.district).toBe('主体建筑南半·东侧')
    expect(supplyCentre.district).toBe('主体建筑以北的供应中心')
  })

  test('rejects degenerate enclosures instead of describing them', () => {
    expect(() => measureEnclosure({ id: 'x', areaSquareMillimetres: 1000, boundary: [] })).toThrow(TypeError)
    expect(() => measureEnclosure({ id: 'x', areaSquareMillimetres: 0, boundary: rectangle(1000, 1000).boundary })).toThrow(TypeError)
  })
})
