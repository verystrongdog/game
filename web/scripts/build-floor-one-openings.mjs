import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

// 来源：design/presentation/二维门窗布置工具.md §一、§三—§五。
const webRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const repositoryRoot = path.resolve(webRoot, '..')
const sources = ['reference/供应中心门窗.json']
const catalogPath = 'data/hospital_ref/floor-one-opening-catalog.json'
const topologyPath = 'data/hospital_ref/floor-one-enclosures.json'
const outputPath = 'data/hospital_ref/floor-one-openings.json'

const readJson = relativePath => JSON.parse(fs.readFileSync(path.join(repositoryRoot, relativePath), 'utf8'))
const pointKey = point => `${point.x},${point.y}`
const wallKey = wall => [pointKey(wall.from), pointKey(wall.to)].sort().join('|')
const openingAxis = placement => placement.orientation === 'horizontal' ? 'x' : 'y'

function requireIntegerPoint(point, label) {
  if (!point || !Number.isInteger(point.x) || !Number.isInteger(point.y)) throw new TypeError(`${label}必须使用整数毫米坐标`)
}

function validatePlacement(placement, components, planarWallKeys, ids) {
  if (!placement?.id || ids.has(placement.id)) throw new Error(`门窗 ID 缺失或重复：${placement?.id || '空'}`)
  ids.add(placement.id)
  const component = components.get(placement.componentId)
  if (!component) throw new Error(`${placement.id} 引用未知组件：${placement.componentId}`)
  requireIntegerPoint(placement.wall?.from, `${placement.id} 墙段起点`)
  requireIntegerPoint(placement.wall?.to, `${placement.id} 墙段终点`)
  requireIntegerPoint(placement.center, `${placement.id} 中心`)
  const horizontal = placement.wall.from.y === placement.wall.to.y
  const vertical = placement.wall.from.x === placement.wall.to.x
  if (!horizontal && !vertical) throw new Error(`${placement.id} 引用非正交墙段`)
  const canonicalWallKey = wallKey(placement.wall)
  if (placement.wallKey !== canonicalWallKey) throw new Error(`${placement.id} 的 wallKey 与墙段不一致`)
  if (!planarWallKeys.has(canonicalWallKey)) throw new Error(`${placement.id} 引用的墙段不在当前平面拓扑中`)
  const expectedOrientation = horizontal ? 'horizontal' : 'vertical'
  if (placement.orientation !== expectedOrientation) throw new Error(`${placement.id} 的方向与墙段不一致`)
  const axis = horizontal ? 'x' : 'y'
  const crossAxis = horizontal ? 'y' : 'x'
  const minimum = Math.min(placement.wall.from[axis], placement.wall.to[axis])
  const maximum = Math.max(placement.wall.from[axis], placement.wall.to[axis])
  if (placement.center[crossAxis] !== placement.wall.from[crossAxis]) throw new Error(`${placement.id} 的中心不在墙线上`)
  if (placement.center[axis] - placement.spanMillimetres / 2 < minimum || placement.center[axis] + placement.spanMillimetres / 2 > maximum) {
    throw new Error(`${placement.id} 越过墙段端点`)
  }
  for (const field of ['kind', 'spanMillimetres', 'heightMillimetres', 'openingType']) {
    if (placement[field] !== component[field]) throw new Error(`${placement.id} 的 ${field} 与组件目录不一致`)
  }
  if (component.kind === 'door' && placement.clearWidthMillimetres !== component.clearWidthMillimetres) {
    throw new Error(`${placement.id} 的通行净宽与组件目录不一致`)
  }
}

function validateNoOverlap(placements) {
  const byWall = Map.groupBy(placements, placement => placement.wallKey)
  for (const wallPlacements of byWall.values()) {
    for (let leftIndex = 0; leftIndex < wallPlacements.length; leftIndex += 1) {
      for (let rightIndex = leftIndex + 1; rightIndex < wallPlacements.length; rightIndex += 1) {
        const left = wallPlacements[leftIndex]
        const right = wallPlacements[rightIndex]
        const axis = openingAxis(left)
        const minimumSeparation = (left.spanMillimetres + right.spanMillimetres) / 2
        if (Math.abs(left.center[axis] - right.center[axis]) < minimumSeparation) {
          throw new Error(`同墙门窗重叠：${left.id} / ${right.id}`)
        }
      }
    }
  }
}

const catalog = readJson(catalogPath)
const topology = readJson(topologyPath)
if (catalog.schema !== 'hospital-opening-catalog/v1' || !Array.isArray(catalog.components)) throw new TypeError('门窗组件目录格式错误')
if (!Array.isArray(topology.planarWalls)) throw new TypeError('一层平面墙段尚未生成')
const components = new Map(catalog.components.map(component => [component.id, component]))
const planarWallKeys = new Set(topology.planarWalls.map(wallKey))
const ids = new Set()
const placements = []

for (const source of sources) {
  const layout = readJson(source)
  if (layout.schema !== 'hospital-opening-layout/v1' || layout.coordinateUnit !== 'millimetre' || !Array.isArray(layout.placements)) {
    throw new TypeError(`${source} 必须是 hospital-opening-layout/v1 毫米坐标数据`)
  }
  for (const placement of layout.placements) {
    validatePlacement(placement, components, planarWallKeys, ids)
    placements.push({ ...placement, sourceFile: source })
  }
}
validateNoOverlap(placements)

const output = {
  _source: sources,
  _generatedBy: 'web/scripts/build-floor-one-openings.mjs',
  _status: 'owner-authored-opening-baseline',
  schema: 'hospital-opening-layout/v1',
  coordinateUnit: 'millimetre',
  placements,
}
fs.writeFileSync(path.join(repositoryRoot, outputPath), `${JSON.stringify(output, null, 2)}\n`)
const doors = placements.filter(placement => placement.kind === 'door').length
const windows = placements.filter(placement => placement.kind === 'window').length
console.log(`Generated ${outputPath}: ${placements.length} openings (${doors} doors, ${windows} windows)`)
