// PROTOTYPE — three presentations over one semantic map, switchable with ?variant=.
// 来源：design/presentation/500床一层跑团地图原型.md §一—§五。
import planUrl from '../../../data/hospital_ref/vector/page-26.svg?url'
import planPreviewUrl from '../../../data/hospital_ref/cache/page-26-web.png?url'
import exteriorWallTopology from '../../../data/hospital_ref/floor-one-exterior-walls.json'
import { EDGE_PAN_MAX_FRAME_SECONDS, edgePanVelocity } from './edge-pan.js'
import { floorOneMap } from './floor-one-map.js'
import { createFloorMapRuntime } from './floor-map-runtime.js'
import {
  axisPosition,
  constrainWallPoint,
  mapPointToMillimetres,
  metricGridValues,
  millimetrePointToMap,
  snapMapPointToMillimetres,
  snapGridStepForZoom,
  yAxesForX,
} from './map-coordinate.js'
import { createWallTrace, serialiseWallTopology } from './wall-trace.js'
import { clampZoom, nextWheelZoom, wheelZoomTarget } from './zoom-motion.js'

const variants = ['atlas', 'tabletop', 'route']
const byId = id => floorOneMap.locations.find(location => location.id === id)
const escapeHtml = value => String(value).replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;')

function mapCoordinate(x, y) {
  const point = mapPointToMillimetres(floorOneMap.coordinateSystem, { x, y })
  return {
    x: point.x / 1000,
    y: point.y / 1000,
  }
}

function coordinateLabel(x, y) {
  const point = mapCoordinate(x, y)
  const signed = value => `${value >= 0 ? '+' : '−'}${Math.abs(value).toFixed(1)}`
  return `X ${signed(point.x)} m · Y ${signed(point.y)} m`
}

function copyCoordinateLabel(x, y) {
  const point = mapCoordinate(x, y)
  return copyMillimetreCoordinateLabel({ x: point.x * 1000, y: point.y * 1000 })
}

function copyMillimetreCoordinateLabel(point, kind = '交点') {
  const signed = value => {
    const metres = (Math.abs(value) / 1000).toFixed(3).replace(/\.?0+$/, '')
    return `${value >= 0 ? '+' : '−'}${metres}`
  }
  return `地图${kind} X ${signed(point.x)} m, Y ${signed(point.y)} m`
}

function routeSvg(view, { labels = false } = {}) {
  const lines = view.connections.map(([a, b]) => {
    const from = byId(a); const to = byId(b)
    return `<line x1="${from.x}" y1="${from.y}" x2="${to.x}" y2="${to.y}" />`
  }).join('')
  const nodes = labels ? view.locations.map(location => `<g class="route-svg-node ${location.current ? 'current' : ''}">
    <circle cx="${location.x}" cy="${location.y}" r="1.35"/><text x="${location.x}" y="${location.y - 2.2}">${escapeHtml(location.name)}</text>
  </g>`).join('') : ''
  return `<svg class="map-routes" viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true"><g>${lines}</g>${nodes}</svg>`
}

function regionSvg(view) {
  const polygons = view.locations.map(location => {
    const stateClass = location.current ? 'current' : location.reachable ? 'reachable' : 'locked'
    const enabled = location.current || location.reachable
    return `<polygon class="map-region ${stateClass}" points="${location.region}" ${enabled ? `data-location="${location.id}" tabindex="0" role="button"` : ''} aria-label="${escapeHtml(location.name)}"><title>${escapeHtml(location.name)}</title></polygon>`
  }).join('')
  return `<svg class="map-regions" viewBox="0 0 100 100" preserveAspectRatio="none" aria-label="可移动区域">${polygons}</svg>`
}

function wallEndpointPosition(point) {
  return millimetrePointToMap(floorOneMap.coordinateSystem, point)
}

function authoredWallLines(topology) {
  return topology.walls.map(wall => {
    const from = wallEndpointPosition(wall.from)
    const to = wallEndpointPosition(wall.to)
    if (!from || !to) return ''
    const geometry = `x1="${from.x}" y1="${from.y}" x2="${to.x}" y2="${to.y}"`
    return `<line class="authored-wall-shadow" ${geometry}/><line class="authored-wall-line" ${geometry}/>`
  }).join('')
}

function gridPath(values, axes, segment) {
  return values.map(value => segment(axisPosition(axes, value))).join('')
}

function snapGridSvg(structuralGrid, seam, stepMillimetres) {
  const majorStep = stepMillimetres * 10
  const splitByWeight = values => ({
    minor: values.filter(value => value % majorStep !== 0),
    major: values.filter(value => value % majorStep === 0),
  })
  const xValues = splitByWeight(metricGridValues(structuralGrid.x, stepMillimetres))
  const mainYValues = splitByWeight(metricGridValues(structuralGrid.y, stepMillimetres))
  const supplyYValues = splitByWeight(metricGridValues(structuralGrid.northSupply.y, stepMillimetres))
  const vertical = values => gridPath(values, structuralGrid.x, position => `M${position},18V80`)
  const mainHorizontal = values => gridPath(values, structuralGrid.y, position => `M${seam.position},${position}H88`)
  const supplyHorizontal = values => gridPath(values, structuralGrid.northSupply.y, position => `M7,${position}H${seam.position}`)
  return `<g class="snap-grid" aria-hidden="true">
    <path class="snap-grid-minor" d="${vertical(xValues.minor)}${mainHorizontal(mainYValues.minor)}${supplyHorizontal(supplyYValues.minor)}" />
    <path class="snap-grid-major" d="${vertical(xValues.major)}${mainHorizontal(mainYValues.major)}${supplyHorizontal(supplyYValues.major)}" />
  </g>`
}

function coordinateSvg(topology, selectedGridPoint, selectedPointKind, interactionMode, zoom, snapGridStep) {
  const { origin: { x, y }, structuralGrid } = floorOneMap.coordinateSystem
  // 来源：design/presentation/500床一层跑团地图原型.md §一·校图坐标系（屏幕直径约 6 CSS px）。
  const markerHalfX = .22
  const markerHalfY = .31
  const dotRadiusX = .08
  const dotRadiusY = .11
  const seam = structuralGrid.x.find(axis => axis.millimetres === structuralGrid.northSupply.northOfXMillimetres)
  const verticalLines = structuralGrid.x.map(axis => `<line class="structural-grid-line east-west-axis" x1="${axis.position}" y1="18" x2="${axis.position}" y2="80" />`).join('')
  const mainHorizontalLines = structuralGrid.y.map(axis => `<line class="structural-grid-line north-south-axis main-grid-axis" x1="${seam.position}" y1="${axis.position}" x2="88" y2="${axis.position}" />`).join('')
  const supplyHorizontalLines = structuralGrid.northSupply.y.map(axis => `<line class="structural-grid-line north-south-axis north-supply-grid-axis" x1="7" y1="${axis.position}" x2="${seam.position}" y2="${axis.position}" />`).join('')
  const intersectionAction = interactionMode === 'snap' ? '点击复制并描墙' : '点击复制坐标'
  const intersections = structuralGrid.x.flatMap(xAxis => yAxesForX(structuralGrid, xAxis.millimetres, true).map(yAxis => {
    const point = { x: xAxis.millimetres, y: yAxis.millimetres }
    const label = copyMillimetreCoordinateLabel(point)
    const selected = selectedPointKind === 'grid' && selectedGridPoint?.x === point.x && selectedGridPoint?.y === point.y
    const active = topology.activeAnchor?.x === point.x && topology.activeAnchor?.y === point.y
    return `<g class="grid-intersection${selected ? ' selected' : ''}${active ? ' wall-anchor' : ''}" data-grid-coordinate data-grid-x="${xAxis.position}" data-grid-y="${yAxis.position}" data-grid-mm-x="${point.x}" data-grid-mm-y="${point.y}" tabindex="0" role="button" aria-label="${label}，${intersectionAction}">
      <ellipse class="grid-intersection-hit" cx="${xAxis.position}" cy="${yAxis.position}" rx="${markerHalfX}" ry="${markerHalfY}" />
      <ellipse class="grid-intersection-dot" cx="${xAxis.position}" cy="${yAxis.position}" rx="${dotRadiusX}" ry="${dotRadiusY}" />
      <title>${label}（${intersectionAction}）</title>
    </g>`
  })).join('')
  const snappedPointPosition = selectedPointKind === 'snap' && selectedGridPoint ? wallEndpointPosition(selectedGridPoint) : null
  const snappedPoint = snappedPointPosition ? `<g class="snap-wall-point" aria-label="最后选择的吸附点">
    <line x1="${snappedPointPosition.x - markerHalfX}" y1="${snappedPointPosition.y}" x2="${snappedPointPosition.x + markerHalfX}" y2="${snappedPointPosition.y}" />
    <line x1="${snappedPointPosition.x}" y1="${snappedPointPosition.y - markerHalfY}" x2="${snappedPointPosition.x}" y2="${snappedPointPosition.y + markerHalfY}" />
  </g>` : ''
  return `<svg class="map-coordinate-system" viewBox="0 0 100 100" preserveAspectRatio="none" aria-label="地图校准坐标系">
    ${interactionMode === 'snap' ? snapGridSvg(structuralGrid, seam, snapGridStep) : ''}
    <g class="structural-grid" aria-hidden="true">${verticalLines}${mainHorizontalLines}${supplyHorizontalLines}</g>
    <line class="coordinate-axis x-axis" x1="7" y1="${y}" x2="93" y2="${y}" />
    <line class="coordinate-axis y-axis" x1="${x}" y1="8" x2="${x}" y2="92" />
    <g class="authored-walls" aria-label="已描墙线">${authoredWallLines(topology)}</g>
    <g class="wall-snap-preview" aria-hidden="true"></g>
    ${snappedPoint}
    <g class="structural-grid-intersections">${intersections}</g>
    <g class="coordinate-origin" aria-label="坐标原点">
      <line x1="${x - markerHalfX}" y1="${y}" x2="${x + markerHalfX}" y2="${y}" />
      <line x1="${x}" y1="${y - markerHalfY}" x2="${x}" y2="${y + markerHalfY}" />
    </g>
    <text class="coordinate-label" x="91" y="${y - 1.2}">+X</text>
    <text class="coordinate-label" x="${x + 1.2}" y="10">+Y</text>
  </svg>`
}

function locationButtons(view, compact = false) {
  return view.locations.map(location => `<button type="button" class="map-location${location.current ? ' current' : ''}${location.reachable ? ' reachable' : ''}" style="--x:${location.x}%;--y:${location.y}%" data-location="${location.id}" title="${escapeHtml(location.name)} · ${coordinateLabel(location.x, location.y)}" ${location.current || location.reachable ? '' : 'disabled'}>
    <i></i><span>${compact ? escapeHtml(location.name.replace('一层', '')) : escapeHtml(location.name)}</span>
  </button>`).join('')
}

function peopleTokens(view, getNpcDossier, large = false) {
  return view.actors.map(person => {
    const location = byId(person.location)
    const dossier = getNpcDossier?.(person.id)
    const displayName = dossier?.displayName || '陌生人'
    const displayMark = dossier?.displayMark || '·'
    const peers = view.actors.filter(actor => actor.location === person.location)
    // 来源：design/presentation/开局剧情逻辑原型.md §3.4；同地点人物标记以 0.9 个地图百分比展开。
    const offset = (peers.findIndex(actor => actor.id === person.id) - (peers.length - 1) / 2) * .9
    return `<button type="button" class="map-person${person.coLocated ? ' co-located' : ''}${large ? ' large' : ''}" style="--x:${location.x + offset}%;--y:${location.y - 1}%" data-person="${person.id}" aria-label="${escapeHtml(displayName)}，位于${escapeHtml(location.name)}，正在${escapeHtml(person.activity)}">
      <b>${escapeHtml(displayMark)}</b><span>${escapeHtml(displayName)}</span>
    </button>`
  }).join('')
}

function playerToken(view) {
  const location = view.currentLocation
  return `<div class="map-player" style="--x:${location.x}%;--y:${location.y}%"><b>你</b><span>当前位置</span></div>`
}

function coordinateReadout() {
  return `<div class="map-coordinate-hud" aria-label="地图坐标">
    <span>图纸坐标</span><output class="map-coordinate-readout" aria-live="polite">拖动画布 · 当前不会生成墙点</output>
  </div>`
}

function camera(state, content) {
  return `<div class="map-viewport"><div class="map-camera" style="--map-scale:${state.zoom};--map-marker-scale:${1 / state.zoom};--map-rotation:${state.rotation}deg;--map-pan-x:${state.panX}px;--map-pan-y:${state.panY}px">${content}</div></div><div class="map-time-filter" aria-hidden="true"></div>${coordinateReadout()}`
}

function planStage(state, view, getNpcDossier, topology, className, alt, compact = false) {
  return camera(state, `<div class="${className}"><img class="map-plan-vector" src="${planUrl}" alt="${alt}" draggable="false"><img class="map-plan-preview" src="${planPreviewUrl}" alt="" aria-hidden="true" draggable="false">${routeSvg(view)}${coordinateSvg(topology, state.selectedGridPoint, state.selectedPointKind, state.interactionMode, state.zoom, state.snapGridStep)}${regionSvg(view)}${locationButtons(view, compact)}${peopleTokens(view, getNpcDossier, compact)}${playerToken(view)}</div>`)
}

function VariantAtlas(state, view, getNpcDossier, topology) {
  return `<div class="map-variant map-atlas">${planStage(state, view, getNpcDossier, topology, 'map-plan-stage', '500床精神专科医院方案一一层矢量平面图')}</div>`
}

function VariantTabletop(state, view, getNpcDossier, topology) {
  return `<div class="map-variant map-tabletop">${planStage(state, view, getNpcDossier, topology, 'tabletop-board', '500床一层矢量平面图桌面底图', true)}</div>`
}

function VariantRoute(state, view, getNpcDossier, topology) {
  return `<div class="map-variant map-route">${camera(state, `<div class="route-network">${routeSvg(view, { labels: true })}${coordinateSvg(topology, state.selectedGridPoint, state.selectedPointKind, state.interactionMode, state.zoom, state.snapGridStep)}${regionSvg(view)}${locationButtons(view, true)}${peopleTokens(view, getNpcDossier, true)}${playerToken(view)}</div>`)}</div>`
}

function currentVariant() {
  const requested = new URLSearchParams(location.search).get('variant')
  return variants.includes(requested) ? requested : 'tabletop'
}

export function createHospitalMapPrototype({ host, scene, getNpcDossier, getTime = () => 'morning', onNpcInspect, onNpcSelect, onMapContext }) {
  const runtime = createFloorMapRuntime(floorOneMap)
  const wallTrace = createWallTrace(exteriorWallTopology)
  const state = { selectedLocation: floorOneMap.initialLocation, selectedPerson: null, selectedGridPoint: null, selectedPointKind: null, interactionMode: 'pan', wallConstraint: 'free', variant: currentVariant(), zoom: 1.35, snapGridStep: snapGridStepForZoom(1.35), rotation: 0, panX: 0, panY: 0 }
  const mapButton = document.querySelector('#mapViewButton')
  const threeButton = document.querySelector('#threeViewButton')
  let mapActive = new URLSearchParams(location.search).get('scene') !== '3d'
  const currentMapView = () => runtime.view(getTime())

  function setMapActive(active) {
    if (!active) {
      stopWheelZoom()
      stopEdgePan()
    }
    mapActive = active
    scene.classList.toggle('map-prototype-active', active)
    host.hidden = !active
    mapButton.classList.toggle('active', active)
    threeButton.classList.toggle('active', !active)
    mapButton.setAttribute('aria-pressed', String(active))
    threeButton.setAttribute('aria-pressed', String(!active))
  }

  function render() {
    const view = currentMapView()
    const topology = wallTrace.snapshot()
    host.dataset.variant = state.variant
    host.innerHTML = state.variant === 'atlas' ? VariantAtlas(state, view, getNpcDossier, topology) : state.variant === 'route' ? VariantRoute(state, view, getNpcDossier, topology) : VariantTabletop(state, view, getNpcDossier, topology)
  }

  function showLocationContext(mapLocation, moved = false) {
    const atmosphere = mapLocation.atmosphere?.[getTime()]
    const sensory = atmosphere ? ` ${atmosphere.sight} ${atmosphere.sound} ${atmosphere.smell}` : ''
    onMapContext({
      locationId: mapLocation.id,
      title: mapLocation.name,
      description: moved ? `你已到达${mapLocation.name}。` : '医院一层活动区域',
      detail: `${mapLocation.summary}${sensory} 粗校坐标：${coordinateLabel(mapLocation.x, mapLocation.y)}。`,
      objective: moved ? `在${mapLocation.name}寻找人物或下一个相邻区域。` : `前往${mapLocation.name}。`,
    })
  }

  function applyCamera() {
    const cameraElement = host.querySelector('.map-camera')
    if (!cameraElement) return
    cameraElement.style.setProperty('--map-scale', state.zoom)
    cameraElement.style.setProperty('--map-marker-scale', 1 / state.zoom)
    cameraElement.style.setProperty('--map-pan-x', `${state.panX}px`)
    cameraElement.style.setProperty('--map-pan-y', `${state.panY}px`)
    cameraElement.style.setProperty('--map-rotation', `${state.rotation}deg`)
  }

  function applyPan(cameraElement = host.querySelector('.map-camera')) {
    if (!cameraElement) return
    cameraElement.style.setProperty('--map-pan-x', `${state.panX}px`)
    cameraElement.style.setProperty('--map-pan-y', `${state.panY}px`)
  }

  function setZoom(nextZoom, clientX, clientY) {
    const previousZoom = state.zoom
    nextZoom = clampZoom(nextZoom)
    if (clientX != null && clientY != null) {
      const rect = host.getBoundingClientRect()
      const pointerX = clientX - rect.left - rect.width / 2
      const pointerY = clientY - rect.top - rect.height / 2
      const ratio = nextZoom / previousZoom
      state.panX = pointerX - (pointerX - state.panX) * ratio
      state.panY = pointerY - (pointerY - state.panY) * ratio
    }
    state.zoom = nextZoom
    const nextGridStep = snapGridStepForZoom(nextZoom)
    if (nextGridStep !== state.snapGridStep) {
      state.snapGridStep = nextGridStep
      if (state.interactionMode === 'snap') render()
      else applyCamera()
    } else applyCamera()
  }

  let wheelFrame = 0
  let wheelTargetZoom = state.zoom
  let wheelAnchor = null

  function stopWheelZoom() {
    if (wheelFrame) cancelAnimationFrame(wheelFrame)
    wheelFrame = 0
    wheelTargetZoom = state.zoom
    wheelAnchor = null
    host.classList.remove('map-zooming')
  }

  function changeZoom(delta, clientX, clientY) {
    stopWheelZoom()
    setZoom(state.zoom + delta, clientX, clientY)
  }

  function runWheelZoomFrame() {
    const nextZoom = nextWheelZoom(state.zoom, wheelTargetZoom)
    setZoom(nextZoom, wheelAnchor?.x, wheelAnchor?.y)
    if (nextZoom === wheelTargetZoom) {
      wheelFrame = 0
      wheelAnchor = null
      host.classList.remove('map-zooming')
      return
    }
    wheelFrame = requestAnimationFrame(runWheelZoomFrame)
  }

  function queueWheelZoom(event) {
    // 来源：design/presentation/500床一层跑团地图原型.md §四；DOM_DELTA_LINE 按 16 px、DOM_DELTA_PAGE 按视口高归一化。
    const deltaY = event.deltaY * (event.deltaMode === 1 ? 16 : event.deltaMode === 2 ? host.clientHeight : 1)
    wheelTargetZoom = wheelZoomTarget(wheelFrame ? wheelTargetZoom : state.zoom, deltaY)
    wheelAnchor = { x: event.clientX, y: event.clientY }
    host.classList.add('map-zooming')
    if (!wheelFrame) wheelFrame = requestAnimationFrame(runWheelZoomFrame)
  }

  function pointOnMap(event) {
    const coordinateLayer = host.querySelector('.map-coordinate-system')
    const matrix = coordinateLayer?.getScreenCTM()
    if (!matrix) return null
    const point = new DOMPoint(event.clientX, event.clientY).matrixTransform(matrix.inverse())
    if (point.x < 0 || point.x > 100 || point.y < 0 || point.y > 100) return null
    return { x: point.x, y: point.y }
  }

  function constrainedWallPoint(mapPoint, exactPoint = null) {
    const anchor = wallTrace.snapshot().activeAnchor
    if (!anchor || state.wallConstraint === 'free') {
      return exactPoint || snapMapPointToMillimetres(floorOneMap.coordinateSystem, mapPoint, state.snapGridStep)
    }
    if (state.wallConstraint === 'horizontal') {
      const point = exactPoint || snapMapPointToMillimetres(floorOneMap.coordinateSystem, mapPoint, state.snapGridStep)
      return constrainWallPoint(anchor, point, state.wallConstraint)
    }
    if (exactPoint) return constrainWallPoint(anchor, exactPoint, state.wallConstraint)
    return snapMapPointToMillimetres(floorOneMap.coordinateSystem, mapPoint, state.snapGridStep, anchor.x)
  }

  function wallDirection(from, to) {
    if (!from || !to) return '起点'
    if (from.y === to.y) return '水平'
    if (from.x === to.x) return '垂直'
    return '斜向'
  }

  function updateSnapPreview(mapPoint) {
    const layer = host.querySelector('.wall-snap-preview')
    if (!layer || state.interactionMode !== 'snap') return null
    const topology = wallTrace.snapshot()
    const point = constrainedWallPoint(mapPoint)
    const anchorPosition = topology.activeAnchor ? wallEndpointPosition(topology.activeAnchor) : null
    const pointPosition = wallEndpointPosition(point)
    // 来源：design/presentation/500床一层跑团地图原型.md §一·校图坐标系（固定屏幕尺寸细十字）。
    const halfX = .22 / state.zoom
    const halfY = .31 / state.zoom
    const previewLine = anchorPosition ? `<line class="wall-preview-shadow" x1="${anchorPosition.x}" y1="${anchorPosition.y}" x2="${pointPosition.x}" y2="${pointPosition.y}"/><line class="wall-preview-line" x1="${anchorPosition.x}" y1="${anchorPosition.y}" x2="${pointPosition.x}" y2="${pointPosition.y}"/>` : ''
    layer.innerHTML = `${previewLine}<line class="wall-preview-cursor" x1="${pointPosition.x - halfX}" y1="${pointPosition.y}" x2="${pointPosition.x + halfX}" y2="${pointPosition.y}"/><line class="wall-preview-cursor" x1="${pointPosition.x}" y1="${pointPosition.y - halfY}" x2="${pointPosition.x}" y2="${pointPosition.y + halfY}"/>`
    const readout = host.querySelector('.map-coordinate-readout')
    if (readout) readout.textContent = `${copyMillimetreCoordinateLabel(point, '吸附点')} · ${wallDirection(topology.activeAnchor, point)} · 网格 ${state.snapGridStep} mm`
    return point
  }

  let edgePanFrame = 0
  let edgePanPointer = null
  let edgePanPreviousTime = null
  let edgePanViewport = null
  let edgePanCamera = null

  function stopEdgePan() {
    if (edgePanFrame) cancelAnimationFrame(edgePanFrame)
    edgePanFrame = 0
    edgePanPointer = null
    edgePanPreviousTime = null
    edgePanViewport = null
    edgePanCamera = null
    host.classList.remove('map-panning')
  }

  function runEdgePanFrame(timestamp) {
    edgePanFrame = 0
    if (!edgePanPointer || state.interactionMode !== 'snap' || !wallTrace.snapshot().activeAnchor) {
      stopEdgePan()
      return
    }
    const rect = edgePanViewport || host.getBoundingClientRect()
    const velocityX = edgePanVelocity(edgePanPointer.clientX, rect.left, rect.right)
    const velocityY = edgePanVelocity(edgePanPointer.clientY, rect.top, rect.bottom)
    if (velocityX === 0 && velocityY === 0) {
      edgePanPreviousTime = null
      edgePanViewport = null
      host.classList.remove('map-panning')
      const mapPoint = pointOnMap(edgePanPointer)
      if (mapPoint) updateSnapPreview(mapPoint)
      return
    }
    host.classList.add('map-panning')
    const elapsed = edgePanPreviousTime == null ? 0 : Math.min((timestamp - edgePanPreviousTime) / 1000, EDGE_PAN_MAX_FRAME_SECONDS)
    edgePanPreviousTime = timestamp
    state.panX -= velocityX * elapsed
    state.panY -= velocityY * elapsed
    applyPan(edgePanCamera)
    edgePanFrame = requestAnimationFrame(runEdgePanFrame)
  }

  function startEdgePan() {
    if (!edgePanFrame && edgePanPointer && state.interactionMode === 'snap' && wallTrace.snapshot().activeAnchor) {
      edgePanViewport = host.getBoundingClientRect()
      edgePanCamera = host.querySelector('.map-camera')
      edgePanFrame = requestAnimationFrame(runEdgePanFrame)
    }
  }

  function writeClipboard(text) {
    const fallbackCopy = () => {
      const fallback = document.createElement('textarea')
      fallback.value = text
      fallback.setAttribute('readonly', '')
      fallback.style.position = 'fixed'
      fallback.style.opacity = '0'
      document.body.append(fallback)
      fallback.select()
      document.execCommand('copy')
      fallback.remove()
    }
    if (navigator.clipboard?.writeText) navigator.clipboard.writeText(text).catch(fallbackCopy)
    else fallbackCopy()
  }

  function wallChangeMessage(change, topology, coordinateText = '') {
    if (change === 'started') return `描墙起点：${coordinateText}；点击下一吸附点生成墙段`
    if (change === 'added') {
      const wall = topology.walls.at(-1)
      return `已生成${wallDirection(wall.from, wall.to)}墙；当前共 ${topology.walls.length} 段，继续点击或按 Esc 结束`
    }
    if (change === 'duplicate') return '该墙段已存在；已从当前交点继续描墙'
    if (change === 'finished') return `已结束描墙，共 ${topology.walls.length} 段`
    if (change === 'undone') return `已撤销末段墙，剩余 ${topology.walls.length} 段`
    if (change === 'cleared') return `已清空本次新增墙线，保留整体外墙 ${topology.walls.length} 段`
    return `墙线未变化，共 ${topology.walls.length} 段`
  }

  function refreshWallPresentation(result, coordinateText = '') {
    const { topology } = result
    host.querySelectorAll('.authored-walls').forEach(layer => { layer.innerHTML = authoredWallLines(topology) })
    host.querySelectorAll('.grid-intersection.wall-anchor').forEach(item => item.classList.remove('wall-anchor'))
    if (topology.activeAnchor) {
      host.querySelector(`[data-grid-mm-x="${topology.activeAnchor.x}"][data-grid-mm-y="${topology.activeAnchor.y}"]`)?.classList.add('wall-anchor')
    }
    const readout = host.querySelector('.map-coordinate-readout')
    if (readout) readout.textContent = wallChangeMessage(result.change, topology, coordinateText)
    host.dispatchEvent(new CustomEvent('walltracechange', { detail: topology }))
    return topology
  }

  function gridPointFromTarget(target) {
    return { x: Number(target.dataset.gridMmX), y: Number(target.dataset.gridMmY) }
  }

  function markCoordinateCopied(target) {
    host.querySelectorAll('.grid-intersection.selected').forEach(item => item.classList.remove('selected'))
    host.querySelectorAll('.snap-wall-point').forEach(item => item.remove())
    target.classList.add('selected')
    state.selectedGridPoint = gridPointFromTarget(target)
    state.selectedPointKind = 'grid'
    const text = copyCoordinateLabel(Number(target.dataset.gridX), Number(target.dataset.gridY))
    return text
  }

  function copyGridCoordinate(target, traceWall = false) {
    const copiedText = markCoordinateCopied(target)
    if (traceWall) {
      const exactPoint = gridPointFromTarget(target)
      const point = constrainedWallPoint({ x: Number(target.dataset.gridX), y: Number(target.dataset.gridY) }, exactPoint)
      const constrained = point.x !== exactPoint.x || point.y !== exactPoint.y
      const text = constrained ? copyMillimetreCoordinateLabel(point, '吸附点') : copiedText
      state.selectedGridPoint = point
      state.selectedPointKind = constrained ? 'snap' : 'grid'
      writeClipboard(text)
      const result = wallTrace.select(point)
      render()
      refreshWallPresentation(result, text)
      startEdgePan()
    }
    else {
      writeClipboard(copiedText)
      const readout = host.querySelector('.map-coordinate-readout')
      if (readout) readout.textContent = `已复制：${copiedText}`
    }
  }

  function selectSnappedPoint(mapPoint) {
    const point = constrainedWallPoint(mapPoint)
    const text = copyMillimetreCoordinateLabel(point, '吸附点')
    state.selectedGridPoint = point
    state.selectedPointKind = 'snap'
    writeClipboard(text)
    const result = wallTrace.select(point)
    render()
    refreshWallPresentation(result, text)
    startEdgePan()
  }

  function setVariant(next) {
    state.variant = next
    const url = new URL(location.href)
    url.searchParams.set('variant', next)
    history.replaceState({}, '', url)
    render()
  }

  function selectLocation(destination) {
    const result = runtime.move(destination, getTime())
    state.selectedLocation = destination
    state.selectedPerson = null
    render()
    showLocationContext(byId(destination), result.moved || result.reason === 'already-there')
  }

  host.addEventListener('click', event => {
    if (suppressNextClick) {
      suppressNextClick = false
      return
    }
    const gridCoordinate = event.target.closest('[data-grid-coordinate]')
    if (gridCoordinate) {
      copyGridCoordinate(gridCoordinate, state.interactionMode === 'snap')
      return
    }
    if (state.interactionMode === 'snap') {
      const point = pointOnMap(event)
      if (point) selectSnappedPoint(point)
      return
    }
    const locationTarget = event.target.closest('[data-location]')
    if (locationTarget) return selectLocation(locationTarget.dataset.location)

    const personButton = event.target.closest('[data-person]')
    if (!personButton) return
    state.selectedPerson = personButton.dataset.person
    const view = currentMapView()
    const person = view.actors.find(item => item.id === state.selectedPerson)
    const context = { coLocated: person.coLocated, locationId: person.location, locationName: byId(person.location).name, activity: person.activity }
    if (onNpcInspect) onNpcInspect(person.id, context)
    else if (person.coLocated) onNpcSelect(person.id, context)
    render()
  })

  host.addEventListener('keydown', event => {
    if (event.key === 'Escape') {
      stopEdgePan()
      refreshWallPresentation(wallTrace.finish())
      return
    }
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'z') {
      event.preventDefault()
      refreshWallPresentation(wallTrace.undo())
      return
    }
    const gridCoordinate = event.target.closest('[data-grid-coordinate]')
    if (gridCoordinate && (event.key === 'Enter' || event.key === ' ')) {
      event.preventDefault()
      copyGridCoordinate(gridCoordinate, state.interactionMode === 'snap')
      return
    }
    const target = event.target.closest('[data-location]')
    if (target && (event.key === 'Enter' || event.key === ' ')) {
      event.preventDefault()
      selectLocation(target.dataset.location)
    }
  })
  host.addEventListener('wheel', event => {
    if (!mapActive) return
    event.preventDefault()
    queueWheelZoom(event)
  }, { passive: false })

  host.addEventListener('pointermove', event => {
    edgePanPointer = { clientX: event.clientX, clientY: event.clientY }
    startEdgePan()
    // 来源：design/presentation/500床一层跑团地图原型.md §四；连续移动只更新相机平移，避免同步 SVG 矩阵反算。
    if (drag || host.classList.contains('map-panning')) return
    const readout = host.querySelector('.map-coordinate-readout')
    const point = pointOnMap(event)
    if (!point || !readout) return
    if (state.interactionMode === 'snap') {
      updateSnapPreview(point)
      return
    }
    readout.textContent = coordinateLabel(point.x, point.y)
  })
  host.addEventListener('pointerleave', () => {
    stopEdgePan()
    const preview = host.querySelector('.wall-snap-preview')
    if (preview) preview.innerHTML = ''
  })

  let drag = null
  let suppressNextClick = false
  host.addEventListener('pointerdown', event => {
    if (state.interactionMode !== 'pan' || event.target.closest('button, [data-location]')) return
    stopWheelZoom()
    drag = { x: event.clientX, y: event.clientY, panX: state.panX, panY: state.panY, id: event.pointerId, moved: false, camera: host.querySelector('.map-camera') }
    host.setPointerCapture(event.pointerId)
    host.classList.add('dragging')
    host.classList.add('map-panning')
  })
  host.addEventListener('pointermove', event => {
    if (!drag || drag.id !== event.pointerId) return
    if (event.clientX !== drag.x || event.clientY !== drag.y) drag.moved = true
    state.panX = drag.panX + event.clientX - drag.x
    state.panY = drag.panY + event.clientY - drag.y
    applyPan(drag.camera)
  })
  const endDrag = event => {
    if (!drag || drag.id !== event.pointerId) return
    suppressNextClick = drag.moved
    drag = null
    host.classList.remove('dragging')
    host.classList.remove('map-panning')
    const point = pointOnMap(event)
    const readout = host.querySelector('.map-coordinate-readout')
    if (point && readout) readout.textContent = coordinateLabel(point.x, point.y)
  }
  host.addEventListener('pointerup', endDrag)
  host.addEventListener('pointercancel', endDrag)

  mapButton.addEventListener('click', () => setMapActive(true))
  threeButton.addEventListener('click', () => setMapActive(false))
  render()
  setMapActive(mapActive)
  showLocationContext(currentMapView().currentLocation, true)
  function resetView() {
    stopWheelZoom()
    state.zoom = 1.35
    state.snapGridStep = snapGridStepForZoom(state.zoom)
    state.rotation = 0
    state.panX = 0
    state.panY = 0
    if (state.interactionMode === 'snap') render()
    else applyCamera()
  }

  return {
    render,
    state: () => ({ ...state, playerLocation: currentMapView().currentLocation.id, wallTopology: wallTrace.snapshot() }),
    show: () => setMapActive(true),
    setMapActive,
    setVariant(next) {
      if (variants.includes(next)) setVariant(next)
    },
    zoomIn: () => changeZoom(.25),
    zoomOut: () => changeZoom(-.25),
    rotateLeft() { state.rotation -= 90; applyCamera() },
    rotateRight() { state.rotation += 90; applyCamera() },
    finishWallTrace() { stopEdgePan(); refreshWallPresentation(wallTrace.finish()) },
    undoWall() { refreshWallPresentation(wallTrace.undo()) },
    clearWalls() { refreshWallPresentation(wallTrace.clear()) },
    setInteractionMode(mode) {
      if (!['pan', 'snap'].includes(mode)) return state.interactionMode
      if (mode === 'pan') stopEdgePan()
      const finishing = mode === 'pan' ? wallTrace.finish() : null
      state.interactionMode = mode
      host.classList.toggle('snap-wall-mode', mode === 'snap')
      render()
      const readout = host.querySelector('.map-coordinate-readout')
      if (readout) readout.textContent = mode === 'snap' ? `吸附描墙 · ${state.snapGridStep} mm 网格 · ${state.wallConstraint === 'free' ? '自由方向' : state.wallConstraint === 'horizontal' ? '水平约束' : '垂直约束'}` : '拖动画布 · 当前不会生成墙点'
      if (finishing?.change === 'finished') host.dispatchEvent(new CustomEvent('walltracechange', { detail: finishing.topology }))
      return state.interactionMode
    },
    setWallConstraint(constraint) {
      if (!['free', 'horizontal', 'vertical'].includes(constraint)) return state.wallConstraint
      state.wallConstraint = constraint
      render()
      const readout = host.querySelector('.map-coordinate-readout')
      if (readout) readout.textContent = `描墙方向：${constraint === 'free' ? '自由' : constraint === 'horizontal' ? '水平' : '垂直'}`
      return state.wallConstraint
    },
    copyWallTopology() {
      const text = serialiseWallTopology(wallTrace.snapshot())
      writeClipboard(text)
      const readout = host.querySelector('.map-coordinate-readout')
      if (readout) readout.textContent = `已复制 ${wallTrace.snapshot().walls.length} 段墙线 JSON`
      return text
    },
    resetView,
  }
}
