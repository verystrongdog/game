// 来源：design/presentation/二维门窗布置工具.md §二—§四。

const clonePoint = point => ({ x: point.x, y: point.y })
const pointKey = point => `${point.x},${point.y}`
const wallKey = wall => [pointKey(wall.from), pointKey(wall.to)].sort().join('|')
const cloneWall = wall => ({ from: clonePoint(wall.from), to: clonePoint(wall.to) })

function validatePoint(point, label) {
  if (!point || !Number.isInteger(point.x) || !Number.isInteger(point.y)) throw new TypeError(`${label}必须使用整数毫米坐标`)
}

function validateCatalog(catalog) {
  if (!Array.isArray(catalog) || !catalog.length) throw new TypeError('门窗目录不得为空')
  const byId = new Map()
  for (const component of catalog) {
    if (!component?.id || !['door', 'window'].includes(component.kind)) throw new TypeError('门窗目录条目缺少合法 id 或 kind')
    if (!Number.isInteger(component.spanMillimetres) || component.spanMillimetres <= 0 || !Number.isInteger(component.heightMillimetres) || component.heightMillimetres <= 0) {
      throw new TypeError(`门窗 ${component.id} 必须提供正整数毫米宽高`)
    }
    if (byId.has(component.id)) throw new TypeError(`门窗目录 id 重复：${component.id}`)
    byId.set(component.id, { sillHeightMillimetres: 0, ...component })
  }
  return byId
}

function validateWalls(walls) {
  if (!Array.isArray(walls)) throw new TypeError('墙线必须是数组')
  return walls.map(wall => {
    validatePoint(wall?.from, '墙线端点')
    validatePoint(wall?.to, '墙线端点')
    if (wall.from.x !== wall.to.x && wall.from.y !== wall.to.y) throw new TypeError('门窗编辑器只接受正交墙线')
    if (pointKey(wall.from) === pointKey(wall.to)) throw new TypeError('门窗编辑器不接受零长度墙线')
    return cloneWall(wall)
  })
}

function projectToWall(point, wall, widthMillimetres) {
  const half = widthMillimetres / 2
  const horizontal = wall.from.y === wall.to.y
  const start = horizontal ? Math.min(wall.from.x, wall.to.x) : Math.min(wall.from.y, wall.to.y)
  const end = horizontal ? Math.max(wall.from.x, wall.to.x) : Math.max(wall.from.y, wall.to.y)
  if (end - start < widthMillimetres) return { fits: false }
  const raw = horizontal ? point.x : point.y
  const along = Math.max(start + half, Math.min(end - half, raw))
  const center = horizontal ? { x: Math.round(along), y: wall.from.y } : { x: wall.from.x, y: Math.round(along) }
  return {
    fits: true,
    center,
    distance: Math.hypot(point.x - center.x, point.y - center.y),
    orientation: horizontal ? 'horizontal' : 'vertical',
  }
}

function overlaps(left, right) {
  if (left.wallKey !== right.wallKey) return false
  const axis = left.orientation === 'horizontal' ? 'x' : 'y'
  const leftHalf = left.spanMillimetres / 2
  const rightHalf = right.spanMillimetres / 2
  return Math.abs(left.center[axis] - right.center[axis]) < leftHalf + rightHalf
}

function nextPlacementNumber(placements) {
  return placements.reduce((maximum, placement) => {
    const match = /^opening-(\d+)$/.exec(placement.id)
    return match ? Math.max(maximum, Number(match[1])) : maximum
  }, 0) + 1
}

export function createOpeningEditor({ catalog, walls, snapDistanceMillimetres, initialLayout = null }) {
  const components = validateCatalog(catalog)
  const availableWalls = validateWalls(walls)
  if (!Number.isInteger(snapDistanceMillimetres) || snapDistanceMillimetres <= 0) throw new TypeError('吸附距离必须是正整数毫米')
  let placements = []
  let selectedComponentId = components.keys().next().value
  let selectedPlacementId = null

  if (initialLayout) {
    if (initialLayout.schema !== 'hospital-opening-layout/v1' || initialLayout.coordinateUnit !== 'millimetre' || !Array.isArray(initialLayout.placements)) {
      throw new TypeError('门窗草稿必须是 hospital-opening-layout/v1')
    }
    placements = initialLayout.placements.map(placement => {
      if (!components.has(placement.componentId)) throw new TypeError(`草稿引用未知门窗：${placement.componentId}`)
      validatePoint(placement.center, '门窗中心')
      return { ...placement, center: clonePoint(placement.center), wall: cloneWall(placement.wall) }
    })
  }
  let nextId = nextPlacementNumber(placements)

  function snapshot() {
    return {
      selectedComponentId,
      selectedPlacementId,
      placements: placements.map(placement => ({ ...placement, center: clonePoint(placement.center), wall: cloneWall(placement.wall) })),
    }
  }

  function selectComponent(componentId) {
    if (!components.has(componentId)) throw new RangeError(`未知门窗组件：${componentId}`)
    selectedComponentId = componentId
    return snapshot()
  }

  function place(point) {
    validatePoint(point, '放置点')
    const component = components.get(selectedComponentId)
    const nearest = availableWalls
      .map(wall => ({ wall, distance: projectToWall(point, wall, 1).distance }))
      .sort((left, right) => left.distance - right.distance)[0]
    if (!nearest || nearest.distance > snapDistanceMillimetres) return { change: 'too-far', snapshot: snapshot() }
    nearest.projection = projectToWall(point, nearest.wall, component.spanMillimetres)
    if (!nearest.projection.fits) return { change: 'no-fit', snapshot: snapshot() }
    const placement = {
      id: `opening-${String(nextId++).padStart(3, '0')}`,
      componentId: component.id,
      kind: component.kind,
      ...(component.leaf ? { leaf: component.leaf } : {}),
      wall: cloneWall(nearest.wall),
      wallKey: wallKey(nearest.wall),
      orientation: nearest.projection.orientation,
      center: nearest.projection.center,
      spanMillimetres: component.spanMillimetres,
      ...(component.clearWidthMillimetres ? { clearWidthMillimetres: component.clearWidthMillimetres } : {}),
      heightMillimetres: component.heightMillimetres,
      sillHeightMillimetres: component.sillHeightMillimetres,
      openingType: component.openingType,
      ...(component.activeLeafWidthMillimetres ? { activeLeafWidthMillimetres: component.activeLeafWidthMillimetres } : {}),
      ...(component.interiorExterior ? { interiorExterior: component.interiorExterior } : {}),
      ...(typeof component.openable === 'boolean' ? { openable: component.openable } : {}),
      accessible: Boolean(component.accessible),
      fireRated: component.fireRated ?? null,
      observationPanel: Boolean(component.observationPanel),
      source: component.sourceKind,
      side: 1,
    }
    if (placements.some(existing => overlaps(existing, placement))) return { change: 'overlap', snapshot: snapshot() }
    placements = [...placements, placement]
    selectedPlacementId = placement.id
    return { change: 'placed', placement: { ...placement }, snapshot: snapshot() }
  }

  function select(id) {
    if (!placements.some(placement => placement.id === id)) return { change: 'missing', snapshot: snapshot() }
    selectedPlacementId = id
    return { change: 'selected', placement: placements.find(placement => placement.id === id), snapshot: snapshot() }
  }

  function flipSelected() {
    const placement = placements.find(item => item.id === selectedPlacementId)
    if (!placement || placement.kind !== 'door') return { change: 'unchanged', snapshot: snapshot() }
    placements = placements.map(item => item.id === placement.id ? { ...item, side: item.side * -1 } : item)
    const changed = placements.find(item => item.id === placement.id)
    return { change: 'flipped', placement: { ...changed }, snapshot: snapshot() }
  }

  function removeSelected() {
    if (!selectedPlacementId) return { change: 'unchanged', snapshot: snapshot() }
    const previousLength = placements.length
    placements = placements.filter(placement => placement.id !== selectedPlacementId)
    selectedPlacementId = null
    return { change: placements.length === previousLength ? 'unchanged' : 'removed', snapshot: snapshot() }
  }

  function clear() {
    const changed = placements.length > 0
    placements = []
    selectedPlacementId = null
    return { change: changed ? 'cleared' : 'unchanged', snapshot: snapshot() }
  }

  function serialise() {
    return JSON.stringify({
      schema: 'hospital-opening-layout/v1',
      coordinateUnit: 'millimetre',
      placements: snapshot().placements,
    }, null, 2)
  }

  return { selectComponent, place, select, flipSelected, removeSelected, clear, snapshot, serialise }
}
