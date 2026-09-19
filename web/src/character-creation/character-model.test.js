import { describe, expect, test } from 'bun:test'
import {
  attributeDescriptions,
  attributeLevels,
  attributeNames,
  developmentDefaultCharacter,
  developmentalDiseases,
  experienceCategories,
} from './character-data.js'
import {
  allExperiences,
  attributeLevelForPoints,
  calculateAttributes,
  getDiseaseCandidates,
  getUnresolvedDiseaseCandidates,
  isDiseaseAvailable,
  selectionBlockReason,
} from './character-model.js'

describe('character creation design mirror', () => {
  test('contains the 48 deduplicated experiences in 8 player-facing categories', () => {
    expect(experienceCategories).toHaveLength(8)
    expect(allExperiences).toHaveLength(48)
    expect(allExperiences.filter(item => item.label.includes('长期照护卧床的人'))).toHaveLength(1)
  })

  test('every experience has a raw net gain of 2 and supports authored +3/-1 tradeoffs', () => {
    for (const experience of allExperiences) {
      expect(Object.values(experience.attributes).reduce((sum, value) => sum + value, 0)).toBe(2)
    }
    expect(allExperiences.some(experience => (
      Object.values(experience.attributes).includes(3)
      && Object.values(experience.attributes).includes(-1)
    ))).toBe(true)
  })

  test('enforces category limit and authored conflicts', () => {
    expect(selectionBlockReason(['volatile-home', 'night-shifts'], 'unsafe-place')).toContain('同类')
    expect(selectionBlockReason(['good-child-role'], 'problem-child')).toContain('互斥')
  })

  test('maps the 10-point scale to the five canonical maturation bands', () => {
    expect([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map(attributeLevelForPoints)).toEqual([
      '笨拙', '笨拙', '笨拙', '协调', '协调', '精通', '精通', '娴熟', '娴熟', '娴熟', '本能',
    ])
    const result = calculateAttributes([
      'volatile-home', 'unsafe-place', 'body-jokes', 'food-rules', 'body-policed',
      'checking-work', 'strict-home', 'poverty', 'work-injury',
    ])
    expect(result.观察).toEqual({ points: 10, level: '本能' })
  })

  test('provides a player-facing capability description for every attribute band', () => {
    for (const name of attributeNames) {
      expect(Object.keys(attributeDescriptions[name])).toEqual(attributeLevels)
      for (const level of attributeLevels) {
        expect(attributeDescriptions[name][level].length).toBeGreaterThan(20)
      }
    }
  })

  test('sums experience deltas before clamping so selection order cannot change the result', () => {
    const ids = [
      'volatile-home', 'chaotic-family', 'fostered', 'repeated-leaving',
      'hard-targets', 'gained-lost', 'no-decisions', 'moving',
    ]
    const forward = calculateAttributes(ids)
    const reverse = calculateAttributes([...ids].reverse())
    expect(forward).toEqual(reverse)
    expect(forward.沟通).toEqual({ points: 10, level: '本能' })
    expect(calculateAttributes(['volatile-home']).沟通).toEqual({ points: 0, level: '笨拙' })
  })

  test('derives candidates from experience while keeping developmental track separate', () => {
    const candidates = getDiseaseCandidates(['volatile-home']).map(item => item.name)
    expect(candidates).toContain('PTSD')
    expect(candidates).not.toContain('ASD')
    expect([...developmentalDiseases]).toEqual(['ASD', 'ADHD'])
  })

  test('surfaces authored mappings that have no card in the 26-disease table', () => {
    expect(getUnresolvedDiseaseCandidates(['heavy-labor'])).toEqual(['慢性疼痛'])
    expect(getUnresolvedDiseaseCandidates(['volatile-home'])).toEqual([])
  })

  test('keeps the development default character legal and fully selected', () => {
    const selected = []
    for (const id of developmentDefaultCharacter.experiences) {
      expect(selectionBlockReason(selected, id)).toBeNull()
      selected.push(id)
    }
    expect(selected).toHaveLength(10)
    for (const disease of developmentDefaultCharacter.diseases) {
      expect(isDiseaseAvailable(disease, selected)).toBe(true)
    }
  })
})
