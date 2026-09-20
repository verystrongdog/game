const clonePoint = point => ({ x: point.x, y: point.y })
const pointKey = point => `${point.x},${point.y}`
const edgeKey = (from, to) => [pointKey(from), pointKey(to)].sort().join('|')

function assertPoint(point) {
  if (!point || !Number.isInteger(point.x) || !Number.isInteger(point.y)) {
    throw new TypeError('墙线端点必须是整数毫米坐标')
  }
  return clonePoint(point)
}

function normaliseWall(wall) {
  const from = assertPoint(wall?.from)
  const to = assertPoint(wall?.to)
  if (from.x === to.x && from.y === to.y) throw new TypeError('墙线不得为零长度')
  if (from.x !== to.x && from.y !== to.y) throw new TypeError('闭环计算当前只接受正交墙线')
  return { from, to }
}

function between(value, first, second) {
  return value >= Math.min(first, second) && value <= Math.max(first, second)
}

function signedTwiceArea(polygon) {
  return polygon.reduce((sum, point, index) => {
    const next = polygon[(index + 1) % polygon.length]
    return sum + point.x * next.y - next.x * point.y
  }, 0)
}

function canonicalBoundary(points) {
  const variants = []
  for (const direction of [points, [...points].reverse()]) {
    for (let index = 0; index < direction.length; index += 1) {
      variants.push([...direction.slice(index), ...direction.slice(0, index)])
    }
  }
  variants.sort((left, right) => {
    const a = left.map(pointKey).join('|')
    const b = right.map(pointKey).join('|')
    return a.localeCompare(b)
  })
  return variants[0]
}

function fnv1a(value) {
  let hash = 0x811c9dc5
  for (let index = 0; index < value.length; index += 1) {
    hash ^= value.charCodeAt(index)
    hash = Math.imul(hash, 0x01000193)
  }
  return (hash >>> 0).toString(16).padStart(8, '0')
}

export function calculateEnclosureTopology(topologies) {
  const uniqueWalls = new Map()
  for (const topology of topologies) {
    if (topology?.schema !== 'hospital-wall-topology/v1' || topology.coordinateUnit !== 'millimetre' || !Array.isArray(topology.walls)) {
      throw new TypeError('闭环输入必须是 hospital-wall-topology/v1 毫米墙线数据')
    }
    for (const sourceWall of topology.walls) {
      const wall = normaliseWall(sourceWall)
      uniqueWalls.set(edgeKey(wall.from, wall.to), wall)
    }
  }

  const walls = [...uniqueWalls.values()]
  const splits = walls.map(wall => new Map([
    [pointKey(wall.from), wall.from],
    [pointKey(wall.to), wall.to],
  ]))

  for (let leftIndex = 0; leftIndex < walls.length; leftIndex += 1) {
    const left = walls[leftIndex]
    const leftVertical = left.from.x === left.to.x
    for (let rightIndex = leftIndex + 1; rightIndex < walls.length; rightIndex += 1) {
      const right = walls[rightIndex]
      const rightVertical = right.from.x === right.to.x
      if (leftVertical !== rightVertical) {
        const vertical = leftVertical ? left : right
        const horizontal = leftVertical ? right : left
        const point = { x: vertical.from.x, y: horizontal.from.y }
        if (between(point.y, vertical.from.y, vertical.to.y) && between(point.x, horizontal.from.x, horizontal.to.x)) {
          splits[leftIndex].set(pointKey(point), point)
          splits[rightIndex].set(pointKey(point), point)
        }
        continue
      }
      if (leftVertical && left.from.x !== right.from.x) continue
      if (!leftVertical && left.from.y !== right.from.y) continue
      for (const point of [left.from, left.to, right.from, right.to]) {
        const onLeft = leftVertical
          ? point.x === left.from.x && between(point.y, left.from.y, left.to.y)
          : point.y === left.from.y && between(point.x, left.from.x, left.to.x)
        const onRight = rightVertical
          ? point.x === right.from.x && between(point.y, right.from.y, right.to.y)
          : point.y === right.from.y && between(point.x, right.from.x, right.to.x)
        if (onLeft) splits[leftIndex].set(pointKey(point), point)
        if (onRight) splits[rightIndex].set(pointKey(point), point)
      }
    }
  }

  const planarEdges = new Map()
  for (let index = 0; index < walls.length; index += 1) {
    const vertical = walls[index].from.x === walls[index].to.x
    const points = [...splits[index].values()].sort((a, b) => vertical ? a.y - b.y : a.x - b.x)
    for (let pointIndex = 1; pointIndex < points.length; pointIndex += 1) {
      const from = points[pointIndex - 1]
      const to = points[pointIndex]
      if (pointKey(from) !== pointKey(to)) planarEdges.set(edgeKey(from, to), { from, to })
    }
  }

  const vertices = new Map()
  const vertex = point => {
    const key = pointKey(point)
    if (!vertices.has(key)) vertices.set(key, { ...point, key, neighbours: [] })
    return vertices.get(key)
  }
  for (const edge of planarEdges.values()) {
    const from = vertex(edge.from)
    const to = vertex(edge.to)
    from.neighbours.push(to)
    to.neighbours.push(from)
  }
  const angle = (from, to) => Math.atan2(to.y - from.y, to.x - from.x)
  for (const item of vertices.values()) item.neighbours.sort((a, b) => angle(item, a) - angle(item, b))

  let connectedComponentCount = 0
  const reached = new Set()
  for (const start of vertices.values()) {
    if (reached.has(start.key)) continue
    connectedComponentCount += 1
    const pending = [start]
    while (pending.length) {
      const current = pending.pop()
      if (reached.has(current.key)) continue
      reached.add(current.key)
      pending.push(...current.neighbours)
    }
  }

  const visitedHalfEdges = new Set()
  const enclosures = []
  for (const from of vertices.values()) {
    for (const to of from.neighbours) {
      const startKey = `${from.key}>${to.key}`
      if (visitedHalfEdges.has(startKey)) continue
      const polygon = []
      let previous = from
      let current = to
      let guard = 0
      while (guard++ <= planarEdges.size * 2 + 2) {
        visitedHalfEdges.add(`${previous.key}>${current.key}`)
        polygon.push(previous)
        const reverseIndex = current.neighbours.findIndex(item => item.key === previous.key)
        const next = current.neighbours[(reverseIndex - 1 + current.neighbours.length) % current.neighbours.length]
        previous = current
        current = next
        if (previous.key === from.key && current.key === to.key) break
      }
      if (guard > planarEdges.size * 2 + 2 || polygon.length < 3) continue
      const areaSquareMillimetres = signedTwiceArea(polygon) / 2
      if (areaSquareMillimetres <= 0) continue
      const boundary = canonicalBoundary(polygon.map(clonePoint))
      const signature = boundary.map(pointKey).join('|')
      enclosures.push({
        id: `f1-enclosure-${fnv1a(signature)}`,
        areaSquareMillimetres,
        boundary,
      })
    }
  }
  enclosures.sort((a, b) => a.id.localeCompare(b.id))
  if (new Set(enclosures.map(item => item.id)).size !== enclosures.length) throw new Error('闭环稳定 ID 发生碰撞')

  const degreeOneEndpoints = [...vertices.values()]
    .filter(item => item.neighbours.length === 1)
    .map(({ x, y }) => ({ x, y }))
    .sort((a, b) => a.x - b.x || a.y - b.y)
  const expectedBoundedFaces = planarEdges.size - vertices.size + connectedComponentCount
  if (expectedBoundedFaces !== enclosures.length) {
    throw new Error(`平面图欧拉复核失败：期望 ${expectedBoundedFaces} 个有界面，实际 ${enclosures.length}`)
  }

  return {
    schema: 'hospital-enclosure-topology/v1',
    coordinateUnit: 'millimetre',
    areaUnit: 'square-millimetre',
    sourceWallCount: walls.length,
    planarEdgeCount: planarEdges.size,
    planarWalls: [...planarEdges.values()].map(edge => ({ from: clonePoint(edge.from), to: clonePoint(edge.to) })),
    vertexCount: vertices.size,
    connectedComponentCount,
    enclosures,
    diagnostics: { degreeOneEndpoints },
  }
}
