// 来源：design/presentation/500床一层跑团地图原型.md §一·校图坐标系。

const clonePoint = point => ({ x: point.x, y: point.y })
const pointKey = point => `${point.x},${point.y}`
const samePoint = (left, right) => left.x === right.x && left.y === right.y
const wallKey = (from, to) => [pointKey(from), pointKey(to)].sort().join('|')

function gridPoint(point) {
  if (!point || !Number.isInteger(point.x) || !Number.isInteger(point.y)) {
    throw new TypeError('墙线端点必须使用当前分区轴网的整数毫米坐标')
  }
  return clonePoint(point)
}

function topologyWalls(topology) {
  if (!topology) return []
  if (topology.schema !== 'hospital-wall-topology/v1' || topology.coordinateUnit !== 'millimetre' || !Array.isArray(topology.walls)) {
    throw new TypeError('初始墙拓扑必须是 hospital-wall-topology/v1 毫米坐标数据')
  }

  const seen = new Set()
  return topology.walls.map(wall => {
    const from = gridPoint(wall?.from)
    const to = gridPoint(wall?.to)
    if (samePoint(from, to)) throw new TypeError('初始墙拓扑不得包含零长度墙段')
    const key = wallKey(from, to)
    if (seen.has(key)) throw new TypeError('初始墙拓扑不得包含重复墙段')
    seen.add(key)
    return { from, to }
  })
}

export function createWallTrace(initialTopology = null) {
  const baselineWalls = topologyWalls(initialTopology)
  let walls = baselineWalls.map(wall => ({ from: clonePoint(wall.from), to: clonePoint(wall.to) }))
  let activeAnchor = null

  function snapshot() {
    return {
      schema: 'hospital-wall-topology/v1',
      coordinateUnit: 'millimetre',
      activeAnchor: activeAnchor ? clonePoint(activeAnchor) : null,
      walls: walls.map(wall => ({ from: clonePoint(wall.from), to: clonePoint(wall.to) })),
    }
  }

  function select(point) {
    const selected = gridPoint(point)
    if (!activeAnchor) {
      activeAnchor = selected
      return { change: 'started', topology: snapshot() }
    }
    if (samePoint(activeAnchor, selected)) {
      activeAnchor = null
      return { change: 'finished', topology: snapshot() }
    }

    const candidateKey = wallKey(activeAnchor, selected)
    const duplicate = walls.some(wall => wallKey(wall.from, wall.to) === candidateKey)
    if (!duplicate) walls = [...walls, { from: clonePoint(activeAnchor), to: selected }]
    activeAnchor = selected
    return { change: duplicate ? 'duplicate' : 'added', topology: snapshot() }
  }

  function finish() {
    const changed = activeAnchor !== null
    activeAnchor = null
    return { change: changed ? 'finished' : 'unchanged', topology: snapshot() }
  }

  function undo() {
    if (walls.length === baselineWalls.length) return { change: 'unchanged', topology: snapshot() }
    const removed = walls.at(-1)
    walls = walls.slice(0, -1)
    activeAnchor = clonePoint(removed.from)
    return { change: 'undone', topology: snapshot() }
  }

  function clear() {
    const changed = walls.length > baselineWalls.length || activeAnchor !== null
    walls = baselineWalls.map(wall => ({ from: clonePoint(wall.from), to: clonePoint(wall.to) }))
    activeAnchor = null
    return { change: changed ? 'cleared' : 'unchanged', topology: snapshot() }
  }

  return { select, finish, undo, clear, snapshot }
}

export function serialiseWallTopology(topology) {
  return JSON.stringify({
    schema: topology.schema,
    coordinateUnit: topology.coordinateUnit,
    walls: topology.walls,
  }, null, 2)
}
