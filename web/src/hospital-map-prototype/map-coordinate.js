// 来源：design/presentation/500床一层跑团地图原型.md §一·校图坐标系。

export function snapGridStepForZoom(zoom) {
  if (zoom < 2) return 1000
  if (zoom < 4) return 500
  if (zoom < 8) return 250
  if (zoom < 16) return 100
  if (zoom < 32) return 50
  return 25
}

export function constrainWallPoint(anchor, point, constraint) {
  if (!anchor || constraint === 'free') return point
  if (constraint === 'horizontal') return { x: point.x, y: anchor.y }
  if (constraint === 'vertical') return { x: anchor.x, y: point.y }
  throw new TypeError(`未知墙线方向约束：${constraint}`)
}

function spanFor(axes, value, readValue) {
  for (let index = 0; index < axes.length - 1; index += 1) {
    const fromValue = readValue(axes[index])
    const toValue = readValue(axes[index + 1])
    if (value >= Math.min(fromValue, toValue) && value <= Math.max(fromValue, toValue)) {
      return [axes[index], axes[index + 1]]
    }
  }

  const firstValue = readValue(axes[0])
  const lastValue = readValue(axes.at(-1))
  const beforeFirst = firstValue <= lastValue ? value < firstValue : value > firstValue
  return beforeFirst ? [axes[0], axes[1]] : [axes.at(-2), axes.at(-1)]
}

export function axisMillimetres(axes, position) {
  const [from, to] = spanFor(axes, position, axis => axis.position)
  const progress = (position - from.position) / (to.position - from.position)
  return from.millimetres + (to.millimetres - from.millimetres) * progress
}

export function axisPosition(axes, millimetres) {
  const exact = axes.find(axis => axis.millimetres === millimetres)
  if (exact) return exact.position
  const [from, to] = spanFor(axes, millimetres, axis => axis.millimetres)
  const progress = (millimetres - from.millimetres) / (to.millimetres - from.millimetres)
  return from.position + (to.position - from.position) * progress
}

export function yAxesForX(structuralGrid, xMillimetres, includeSeamAlternates = false) {
  const { northSupply } = structuralGrid
  if (xMillimetres < northSupply.northOfXMillimetres) return northSupply.y
  if (includeSeamAlternates && xMillimetres === northSupply.northOfXMillimetres) {
    const byCoordinate = new Map([...structuralGrid.y, ...northSupply.y].map(axis => [axis.millimetres, axis]))
    return [...byCoordinate.values()].sort((left, right) => left.position - right.position)
  }
  return structuralGrid.y
}

export function mapPointToMillimetres(coordinateSystem, point) {
  const { structuralGrid } = coordinateSystem
  const x = Math.round(axisMillimetres(structuralGrid.x, point.x))
  const y = Math.round(axisMillimetres(yAxesForX(structuralGrid, x), point.y))
  return { x, y }
}

export function snapMapPointToMillimetres(coordinateSystem, point, stepMillimetres, fixedX = null) {
  const { structuralGrid } = coordinateSystem
  const x = fixedX ?? Math.round(axisMillimetres(structuralGrid.x, point.x) / stepMillimetres) * stepMillimetres
  const y = Math.round(axisMillimetres(yAxesForX(structuralGrid, x), point.y) / stepMillimetres) * stepMillimetres
  return { x, y }
}

export function metricGridValues(axes, stepMillimetres) {
  const values = axes.map(axis => axis.millimetres)
  const minimum = Math.min(...values)
  const maximum = Math.max(...values)
  const first = Math.ceil(minimum / stepMillimetres) * stepMillimetres
  const result = []
  for (let value = first; value <= maximum; value += stepMillimetres) result.push(value)
  return result
}

export function millimetrePointToMap(coordinateSystem, point) {
  const { structuralGrid } = coordinateSystem
  return {
    x: axisPosition(structuralGrid.x, point.x),
    y: axisPosition(yAxesForX(structuralGrid, point.x, true), point.y),
  }
}
