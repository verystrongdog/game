import { describe, expect, test } from 'bun:test'
import { readFileSync } from 'node:fs'
import { npcDialogues } from '../dialogue/npcs/index.js'
import {
  NPC_PLACEMENT_STATUS,
  locationLabels,
  npcPlacements,
  placementFor,
  placementsAtTime,
  unmappedLocations,
  validatePlacements,
} from './npc-placements.js'

// 来源：design/presentation/500床一层跑团地图原型.md §2.3；驻地依据 design/spec/material/NPC生态台账.md。
const topology = JSON.parse(readFileSync(new URL('../../../data/hospital_ref/floor-one-enclosures.json', import.meta.url), 'utf8'))
const npcIds = npcDialogues.map(npc => npc.id)
const enclosureIds = topology.enclosures.map(enclosure => enclosure.id)

describe('floor-one NPC placements', () => {
  test('only places people and enclosures that actually exist', () => {
    expect(NPC_PLACEMENT_STATUS).toBe('prototype-placeholder-not-canon')
    expect(() => validatePlacements({ npcIds, enclosureIds })).not.toThrow()
    expect(npcPlacements).toHaveLength(11)
    expect(new Set(npcPlacements.map(placement => placement.npcId)).size).toBe(npcDialogues.length)
  })

  test('rejects unknown people, unknown enclosures, duplicate slots, and missing basis', () => {
    const fixture = { time: 'morning', locationId: 'nurse_station', basis: 'fixture' }
    expect(() => validatePlacements({ placements: [{ ...fixture, npcId: 'ghost', enclosureId: enclosureIds[0] }], npcIds, enclosureIds })).toThrow('不存在的人物')
    expect(() => validatePlacements({ placements: [{ ...fixture, npcId: npcIds[0], enclosureId: 'f1-enclosure-nope' }], npcIds, enclosureIds })).toThrow('不存在的几何闭环')
    expect(() => validatePlacements({ placements: [{ ...fixture, npcId: npcIds[0], enclosureId: enclosureIds[0], locationId: 'moon' }], npcIds, enclosureIds })).toThrow('未登记的语义地点')
    expect(() => validatePlacements({ placements: [{ ...fixture, time: 'dawn', npcId: npcIds[0], enclosureId: enclosureIds[0] }], npcIds, enclosureIds })).toThrow('未登记的时段')
    expect(() => validatePlacements({ placements: [{ ...fixture, npcId: npcIds[0], enclosureId: enclosureIds[0] }, { ...fixture, npcId: npcIds[0], enclosureId: enclosureIds[1] }], npcIds, enclosureIds })).toThrow('同一时段只能有一处落位')
    expect(() => validatePlacements({ placements: [{ time: 'morning', locationId: 'nurse_station', npcId: npcIds[0], enclosureId: enclosureIds[0] }], npcIds, enclosureIds })).toThrow('缺少依据说明')
  })

  test('keeps every declared activity byte-identical to the dialogue data', () => {
    for (const placement of npcPlacements.filter(item => item.activity)) {
      const npc = npcDialogues.find(item => item.id === placement.npcId)
      const matching = (npc.situations || []).filter(situation =>
        situation.requires.times?.includes(placement.time)
        && situation.requires.locations?.includes(placement.locationId)
        && situation.requires.activities?.includes(placement.activity))
      expect(matching.length).toBeGreaterThan(0)
    }
  })

  test('answers every situation in the dialogue data with a placement or a registered gap', () => {
    for (const npc of npcDialogues) {
      for (const situation of npc.situations || []) {
        const [activity] = situation.requires.activities || []
        const placed = (situation.requires.locations || []).some(locationId => (situation.requires.times || []).some(time =>
          placementFor(npc.id, time)?.locationId === locationId && placementFor(npc.id, time)?.activity === activity))
        const registeredGap = (situation.requires.locations || []).every(locationId =>
          unmappedLocations.some(item => item.locationId === locationId && item.npcId === npc.id))
        expect({ npc: npc.id, node: situation.node, answered: placed || registeredGap }).toMatchObject({ answered: true })
      }
    }
  })

  test('keeps one marker per person per time slot and never stacks two markers exactly', () => {
    for (const time of ['morning', 'afternoon', 'night']) {
      const slots = placementsAtTime(time)
      const fingerprints = slots.map(placement => `${placement.enclosureId}@${placement.offset?.x || 0},${placement.offset?.y || 0}`)
      expect(new Set(fingerprints).size).toBe(fingerprints.length)
      for (const placement of slots) {
        expect(locationLabels[placement.locationId]).toBeTruthy()
      }
    }
    expect(placementsAtTime('morning').map(item => item.npcId)).toEqual(['zheng_xiaomin', 'wu_tong', 'zhou_weiguo', 'tang_nianan'])
    expect(placementsAtTime('night').map(item => item.npcId)).toEqual(['tan_lijuan', 'wu_tong', 'zhou_weiguo', 'tang_nianan'])
  })

  test('registers locations the floor plan cannot host yet', () => {
    expect(unmappedLocations).toEqual([
      { locationId: 'basketball_court', npcId: 'wu_tong', reason: expect.stringContaining('户外') },
    ])
    expect(placementFor('wu_tong', 'afternoon')).toBeNull()
    expect(placementFor('zheng_xiaomin', 'night')).toBeNull()
  })
})
