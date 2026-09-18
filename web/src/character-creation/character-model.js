import {
  attributeLevels,
  attributeNames,
  developmentalDiseases,
  diseases,
  experienceCategories,
  experienceConflicts,
} from './character-data.js'

// 来源：design/entities/疾病特长.md §2.2 / §3.1（10 段、同类 2 段、单段原始净值 +2、属性最终限制 0–10）。
export const EXPERIENCE_LIMIT = 10
export const CATEGORY_LIMIT = 2
export const ATTRIBUTE_CAP = 10

export function attributeLevelForPoints(points) {
  const clamped = Math.max(0, Math.min(ATTRIBUTE_CAP, points))
  if (clamped === 10) return attributeLevels[4]
  if (clamped >= 7) return attributeLevels[3]
  if (clamped >= 5) return attributeLevels[2]
  if (clamped >= 3) return attributeLevels[1]
  return attributeLevels[0]
}

export const allExperiences = experienceCategories.flatMap(category => (
  category.experiences.map(experience => ({ ...experience, categoryId: category.id }))
))

const experienceById = new Map(allExperiences.map(experience => [experience.id, experience]))
const categoryByExperience = new Map(allExperiences.map(experience => [experience.id, experience.categoryId]))
const conflictByExperience = new Map()

for (const [left, right] of experienceConflicts) {
  conflictByExperience.set(left, right)
  conflictByExperience.set(right, left)
}

export function selectionBlockReason(selectedIds, experienceId) {
  const selected = new Set(selectedIds)
  if (selected.has(experienceId)) return null
  if (selected.size >= EXPERIENCE_LIMIT) return `最多选择 ${EXPERIENCE_LIMIT} 段经历`

  const categoryId = categoryByExperience.get(experienceId)
  const categoryCount = [...selected].filter(id => categoryByExperience.get(id) === categoryId).length
  if (categoryCount >= CATEGORY_LIMIT) return `同类最多选择 ${CATEGORY_LIMIT} 段经历`

  const conflictingId = conflictByExperience.get(experienceId)
  if (conflictingId && selected.has(conflictingId)) {
    return `与你选择的「${experienceById.get(conflictingId).label}」互斥`
  }
  return null
}

export function calculateAttributes(selectedIds) {
  const totals = Object.fromEntries(attributeNames.map(name => [name, 0]))
  for (const id of selectedIds) {
    const experience = experienceById.get(id)
    if (!experience) continue
    for (const [name, amount] of Object.entries(experience.attributes)) {
      totals[name] += amount
    }
  }
  return Object.fromEntries(attributeNames.map(name => {
    const points = Math.max(0, Math.min(ATTRIBUTE_CAP, totals[name]))
    return [name, { points, level: attributeLevelForPoints(points) }]
  }))
}

export function getDiseaseCandidates(selectedIds) {
  const names = new Set()
  for (const id of selectedIds) {
    experienceById.get(id)?.diseases.forEach(name => names.add(name))
  }
  return diseases.filter(disease => names.has(disease.name))
}

export function getUnresolvedDiseaseCandidates(selectedIds) {
  const knownNames = new Set(diseases.map(disease => disease.name))
  const unresolvedNames = new Set()
  for (const id of selectedIds) {
    for (const name of experienceById.get(id)?.diseases || []) {
      if (!knownNames.has(name)) unresolvedNames.add(name)
    }
  }
  return [...unresolvedNames]
}

export function isDiseaseAvailable(diseaseName, selectedIds) {
  return developmentalDiseases.has(diseaseName)
    || getDiseaseCandidates(selectedIds).some(disease => disease.name === diseaseName)
}

export function getExperience(id) {
  return experienceById.get(id)
}
