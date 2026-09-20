import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { calculateEnclosureTopology } from '../src/hospital-map-prototype/enclosure-topology.js'

const webRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const repositoryRoot = path.resolve(webRoot, '..')
const sources = [
  'reference/墙线.json',
  'reference/新增供应中心墙线.json',
  'reference/新增住院部墙线.json',
  'reference/新增门诊部墙线.json',
]
const topologies = sources.map(source => JSON.parse(fs.readFileSync(path.join(repositoryRoot, source), 'utf8')))
const pointKey = point => `${point.x},${point.y}`
const wallKey = wall => [pointKey(wall.from), pointKey(wall.to)].sort().join('|')
const rawWalls = new Map(topologies.flatMap(topology => topology.walls).map(wall => [wallKey(wall), wall]))
const rawSourceWallCount = rawWalls.size
const repairSource = 'data/hospital_ref/floor-one-wall-topology-repairs.json'
const repairs = JSON.parse(fs.readFileSync(path.join(repositoryRoot, repairSource), 'utf8'))
if (repairs.schema !== 'hospital-wall-topology-repairs/v1' || !Array.isArray(repairs.endpointReplacements) || !Array.isArray(repairs.supplementalWalls)) {
  throw new TypeError('墙线拓扑修正数据必须是 hospital-wall-topology-repairs/v1')
}
const replacementByPoint = new Map(repairs.endpointReplacements.map(item => [pointKey(item.from), item.to]))
const usedReplacements = new Set()
const repairedWalls = new Map()
for (const wall of rawWalls.values()) {
  const replace = point => {
    const key = pointKey(point)
    if (!replacementByPoint.has(key)) return point
    usedReplacements.add(key)
    return replacementByPoint.get(key)
  }
  const repairedWall = { from: replace(wall.from), to: replace(wall.to) }
  if (pointKey(repairedWall.from) === pointKey(repairedWall.to)) throw new Error(`端点修正产生零长度墙线：${wallKey(wall)}`)
  repairedWalls.set(wallKey(repairedWall), repairedWall)
}
const unusedReplacements = [...replacementByPoint.keys()].filter(key => !usedReplacements.has(key))
if (replacementByPoint.size !== repairs.endpointReplacements.length || unusedReplacements.length) {
  throw new Error(`端点修正重复或未命中源墙线：${unusedReplacements.join('、') || '存在重复坐标'}`)
}
for (const wall of repairs.supplementalWalls) {
  const key = wallKey(wall)
  if (repairedWalls.has(key)) throw new Error(`补充墙线已存在：${key}`)
  repairedWalls.set(key, wall)
}
const repairedTopology = {
  schema: 'hospital-wall-topology/v1',
  coordinateUnit: 'millimetre',
  walls: [...repairedWalls.values()],
}
const result = calculateEnclosureTopology([repairedTopology])
const assessmentSource = 'data/hospital_ref/floor-one-degree-one-assessments.json'
const assessmentData = JSON.parse(fs.readFileSync(path.join(repositoryRoot, assessmentSource), 'utf8'))
if (assessmentData.schema !== 'hospital-degree-one-assessments/v1' || !Array.isArray(assessmentData.assessments)) {
  throw new TypeError('一度端点复核数据必须是 hospital-degree-one-assessments/v1')
}
const endpointKeys = new Set(result.diagnostics.degreeOneEndpoints.map(pointKey))
const assessmentKeys = new Set(assessmentData.assessments.map(item => pointKey(item.point)))
const unknownClassifications = assessmentData.assessments
  .filter(item => !Object.hasOwn(assessmentData.classifications, item.classification))
  .map(item => `${pointKey(item.point)}=${item.classification}`)
const missingAssessments = [...endpointKeys].filter(key => !assessmentKeys.has(key))
const staleAssessments = [...assessmentKeys].filter(key => !endpointKeys.has(key))
if (assessmentKeys.size !== assessmentData.assessments.length || missingAssessments.length || staleAssessments.length || unknownClassifications.length) {
  throw new Error(`一度端点复核数据与拓扑不一致：缺少 ${missingAssessments.join('、') || '无'}；失效 ${staleAssessments.join('、') || '无'}；未知类别 ${unknownClassifications.join('、') || '无'}`)
}
const output = {
  _source: sources,
  _generatedBy: 'web/scripts/build-floor-one-enclosures.mjs',
  _repairSource: repairSource,
  _rawSourceWallCount: rawSourceWallCount,
  _assessmentSource: assessmentSource,
  _status: 'geometric-enclosures-not-yet-classified-as-rooms',
  ...result,
}
output.diagnostics.degreeOneEndpointAssessments = assessmentData.assessments
output.diagnostics.degreeOneClassifications = assessmentData.classifications
const outputPath = path.join(repositoryRoot, 'data/hospital_ref/floor-one-enclosures.json')
fs.writeFileSync(outputPath, `${JSON.stringify(output, null, 2)}\n`)
console.log(`Generated ${path.relative(repositoryRoot, outputPath)}: ${result.enclosures.length} enclosures, ${assessmentData.assessments.length} assessed degree-one endpoints`)
