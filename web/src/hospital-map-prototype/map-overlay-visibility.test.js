import { describe, expect, test } from 'bun:test'
import { readFileSync } from 'node:fs'
import { floorOneMap } from './floor-one-map.js'

const css = readFileSync(new URL('./hospital-map-prototype.css', import.meta.url), 'utf8')
const source = readFileSync(new URL('./hospital-map-prototype.js', import.meta.url), 'utf8')
const zoomMotionSource = readFileSync(new URL('./zoom-motion.js', import.meta.url), 'utf8')
const prototypeHtml = readFileSync(new URL('../../../design/presentation/叙事界面原型.html', import.meta.url), 'utf8')
const planPreviewPng = readFileSync(new URL('../../../data/hospital_ref/cache/page-26-web.png', import.meta.url))
const enclosureTopology = JSON.parse(readFileSync(new URL('../../../data/hospital_ref/floor-one-enclosures.json', import.meta.url), 'utf8'))
const topologyRepairs = JSON.parse(readFileSync(new URL('../../../data/hospital_ref/floor-one-wall-topology-repairs.json', import.meta.url), 'utf8'))
const openingCatalog = JSON.parse(readFileSync(new URL('../../../data/hospital_ref/floor-one-opening-catalog.json', import.meta.url), 'utf8'))
const baselineOpenings = JSON.parse(readFileSync(new URL('../../../data/hospital_ref/floor-one-openings.json', import.meta.url), 'utf8'))

describe('map coordinate overlay', () => {
  test('renders the structural grid and keeps non-scaling strokes visibly wide', () => {
    expect(source).toContain('structural-grid-line')
    expect(css).toMatch(/\.structural-grid-line[^}]*stroke-width:\s*1(?:\.\d+)?px/)
    expect(css).toMatch(/\.coordinate-axis[^}]*stroke-width:\s*1(?:\.\d+)?px/)
  })

  test('connects the overall east-west axes across the plan', () => {
    const axes = floorOneMap.coordinateSystem.structuralGrid.x
    expect(Math.min(...axes.map(axis => axis.position))).toBeLessThan(10)
    expect(Math.max(...axes.map(axis => axis.position))).toBeGreaterThan(85)
    expect(axes.map(axis => axis.position)).toContain(floorOneMap.coordinateSystem.origin.x)
  })

  test('maps percentage coordinates across the full non-square floor plan', () => {
    const overlayCount = source.match(/preserveAspectRatio="none"/g)?.length ?? 0
    expect(overlayCount).toBe(3)
  })

  test('makes every grid intersection addressable and copyable', () => {
    expect(source).toContain('data-grid-coordinate')
    expect(source).toContain('copyCoordinateLabel')
    expect(source).toContain('navigator.clipboard?.writeText')
    expect(css).toMatch(/\.grid-intersection-hit\s*\{[^}]*pointer-events:\s*all/)
  })

  test('uses compact authored feedback instead of the stretched native SVG focus disc', () => {
    // 来源：design/presentation/500床一层跑团地图原型.md §一·校图坐标系（仅突出最后选中的交点）。
    expect(css).toMatch(/\.grid-intersection\s*\{[^}]*outline:\s*none/)
    expect(source).toContain('class="grid-intersection-hit"')
    expect(source).toContain('<ellipse class="grid-intersection-hit"')
    expect(css).toContain('transform: scale(var(--map-marker-scale))')
    expect(css).toContain('.grid-intersection:focus-visible .grid-intersection-dot')
    expect(css).not.toContain('.grid-intersection:focus .grid-intersection-dot')
  })

  test('never uses the browser native SVG focus outline for selectable rooms', () => {
    // 来源：design/presentation/叙事界面布局.md §四、500床一层跑团地图原型.md §2.1。
    const enclosureRule = css.match(/\.enclosure-shape\s*\{[^}]*\}/)?.[0] || ''
    const selectedRule = css.match(/\.enclosure-shape\.selected\s*\{[^}]*\}/)?.[0] || ''
    expect(enclosureRule).toMatch(/outline:\s*none/)
    expect(enclosureRule).toMatch(/vector-effect:\s*non-scaling-stroke/)
    expect(selectedRule).not.toMatch(/stroke:\s*(?:black|#000(?:000)?)/)
    expect(css).toContain('.enclosure-shape:focus-visible')
  })

  test('renders reusable millimetre wall topology from successive grid clicks', () => {
    expect(source).toContain("import { createWallTrace, serialiseWallTopology } from './wall-trace.js'")
    expect(source).toContain("import exteriorWallTopology from '../../../data/hospital_ref/floor-one-exterior-walls.json'")
    expect(source).toContain('createWallTrace(exteriorWallTopology)')
    expect(source).toContain('data-grid-mm-x')
    expect(source).toContain('class="authored-walls"')
    expect(source).toContain('wallTrace.select(point)')
    expect(source).toContain('copyWallTopology()')
    expect(css).toMatch(/\.authored-wall-line\s*\{[^}]*vector-effect:\s*non-scaling-stroke|\.authored-wall-shadow, \.authored-wall-line\s*\{[^}]*vector-effect:\s*non-scaling-stroke/)
    expect(css).toMatch(/\.authored-wall-shadow\s*\{[^}]*stroke-width:\s*2\.5px/)
    expect(css).toMatch(/\.authored-wall-line\s*\{[^}]*stroke-width:\s*1px/)
  })

  test('separates snapping and panning while rendering a metric SVG snap grid', () => {
    expect(prototypeHtml).toContain('data-dev-wall-mode="pan"')
    expect(prototypeHtml).toContain('data-dev-wall-mode="snap"')
    expect(source).toContain("copyMillimetreCoordinateLabel(point, '吸附点')")
    expect(source).toContain('snapMapPointToMillimetres(floorOneMap.coordinateSystem, mapPoint, state.snapGridStep)')
    expect(source).toContain("interactionMode: 'pan'")
    expect(source).toContain("interactionMode === 'snap' ? snapGridSvg")
    expect(source).toContain('suppressNextClick = drag.moved')
    expect(source).toContain('applyPan(drag.camera)')
    expect(css).toContain('.hospital-map-prototype.snap-wall-mode')
    expect(css).toContain('.snap-grid-minor')
    expect(css).toContain('.snap-grid-major')
    expect(css).toMatch(/\.snap-grid-minor\s*\{[^}]*stroke-width:\s*calc\(\.3px \* var\(--map-marker-scale\)\)/)
    expect(css).toMatch(/\.snap-grid-major\s*\{[^}]*stroke-width:\s*calc\(\.55px \* var\(--map-marker-scale\)\)/)
    expect(css).toContain('.snap-wall-point')
    expect(source).toContain('wall-snap-preview')
    expect(prototypeHtml).toContain('data-dev-wall-constraint="horizontal"')
    expect(prototypeHtml).toContain('data-dev-wall-constraint="vertical"')
  })

  test('pans at viewport edges only while an anchored wall trace is active', () => {
    expect(source).toContain("import { EDGE_PAN_MAX_FRAME_SECONDS, edgePanVelocity } from './edge-pan.js'")
    expect(source).toContain("state.interactionMode !== 'snap' || !wallTrace.snapshot().activeAnchor")
    expect(source).toContain('state.panX -= velocityX * elapsed')
    expect(source).toContain('state.panY -= velocityY * elapsed')
    expect(source).toContain("host.classList.add('map-panning')")
    expect(source).toContain('applyPan(edgePanCamera)')
    expect(source).toContain("if (drag || host.classList.contains('map-panning')) return")
    expect(css).toContain('.hospital-map-prototype.map-panning .map-camera')
    expect(css).toContain('.hospital-map-prototype.map-panning .map-plan-vector')
    expect(css).toContain('.hospital-map-prototype.map-panning .map-plan-preview')
    expect(css).toContain('.hospital-map-prototype.map-panning .wall-snap-preview')
    expect(css).toContain('.hospital-map-prototype.map-panning .map-location.reachable i')
    expect(source).toContain("host.addEventListener('pointerleave'")
  })

  test('does not capture a coordinate click until pointer movement becomes a drag', () => {
    // 来源：design/presentation/500床一层跑团地图原型.md §一·校图坐标系。
    const pointerDownStart = source.indexOf("host.addEventListener('pointerdown'")
    const pointerMoveStart = source.indexOf("host.addEventListener('pointermove'", pointerDownStart)
    const pointerUpStart = source.indexOf("host.addEventListener('pointerup'", pointerMoveStart)
    const pointerDownHandler = source.slice(pointerDownStart, pointerMoveStart)
    const dragPointerMoveHandler = source.slice(pointerMoveStart, pointerUpStart)
    expect(pointerDownHandler).not.toContain('setPointerCapture')
    expect(dragPointerMoveHandler).toContain('MAP_DRAG_START_DISTANCE_CSS_PIXELS')
    expect(dragPointerMoveHandler).toContain('setPointerCapture')
  })

  test('uses authored ruler distances instead of page-scale interpolation', () => {
    const { structuralGrid, origin } = floorOneMap.coordinateSystem
    expect(structuralGrid.x.every(axis => Number.isInteger(axis.millimetres))).toBe(true)
    expect(structuralGrid.y.every(axis => Number.isInteger(axis.millimetres))).toBe(true)
    expect(structuralGrid.northSupply.y.every(axis => Number.isInteger(axis.millimetres))).toBe(true)
    expect(structuralGrid.x.find(axis => axis.position === origin.x)?.millimetres).toBe(0)
    expect(structuralGrid.y.find(axis => axis.position === origin.y)?.millimetres).toBe(0)
    expect(structuralGrid.x.find(axis => axis.position === 49.3754)?.millimetres).toBe(7500)
    expect(structuralGrid.y.find(axis => axis.position === 52.5933)?.millimetres).toBe(6900)
    expect(structuralGrid.x.at(-1)).toEqual({ position: 87.1751, millimetres: 102800 })
  })

  test('includes the owner-specified east-west axes at X -40.7 m, +20.5 m, and +82.125 m', () => {
    // 来源：design/presentation/500床一层跑团地图原型.md §一·校图坐标系。
    expect(floorOneMap.coordinateSystem.structuralGrid.x).toContainEqual({ position: 30.2492, millimetres: -40700 })
    expect(floorOneMap.coordinateSystem.structuralGrid.x).toContainEqual({ position: 54.5269, millimetres: 20500 })
    expect(floorOneMap.coordinateSystem.structuralGrid.x).toContainEqual({ position: 78.9744, millimetres: 82125 })
  })

  test('includes the owner-specified north-south axes at Y +3.45 m and +51.75 m', () => {
    // 来源：design/presentation/500床一层跑团地图原型.md §一·校图坐标系。
    expect(floorOneMap.coordinateSystem.structuralGrid.y).toContainEqual({ position: 54.5312, millimetres: 3450 })
    expect(floorOneMap.coordinateSystem.structuralGrid.y).toContainEqual({ position: 27.4366, millimetres: 51750 })
  })

  test('switches to the northernmost ruler grid inside the north supply area', () => {
    // 来源：design/presentation/500床一层跑团地图原型.md §一·校图坐标系。
    const { structuralGrid } = floorOneMap.coordinateSystem
    expect(structuralGrid.northSupply.northOfXMillimetres).toBe(-57700)
    expect(structuralGrid.northSupply.y.map(axis => axis.millimetres)).toEqual([
      19500, 12000, 4500, -3000, -10500, -18000, -25500, -33000, -40500,
    ])
    expect(source).toContain('yAxesForX(structuralGrid, xAxis.millimetres, true)')
    expect(source).toContain('class="structural-grid-line north-south-axis main-grid-axis"')
    expect(source).toContain('class="structural-grid-line north-south-axis north-supply-grid-axis"')
    expect(source).toContain('x1="${seam.position}"')
    expect(source).toContain('x2="${seam.position}"')
  })

  test('does not invent semantic rooms, routes, or actor positions before interior walls are traced', () => {
    expect(floorOneMap.initialLocation).toBeNull()
    expect(floorOneMap.locations).toEqual([])
    expect(floorOneMap.connections).toEqual([])
    expect(floorOneMap.actors).toEqual([])
  })

  test('keeps assessed degree-one endpoints in diagnostics without rendering legacy coloured points', () => {
    expect(enclosureTopology.enclosures).toHaveLength(189)
    expect(enclosureTopology.diagnostics.degreeOneEndpoints).toHaveLength(9)
    expect(enclosureTopology.diagnostics.degreeOneEndpointAssessments).toHaveLength(9)
    const classificationCounts = enclosureTopology.diagnostics.degreeOneEndpointAssessments.reduce((counts, item) => ({
      ...counts,
      [item.classification]: (counts[item.classification] || 0) + 1,
    }), {})
    expect(classificationCounts).toEqual({
      'open-boundary-edge': 4,
      'door-opening-edge': 3,
      'partition-termination': 2,
    })
    expect(source).toContain('class="enclosure-shape')
    expect(source).not.toContain('degree-one-endpoint')
    expect(source).not.toContain('data-degree-one-classification')
    expect(source).toContain('setInspectionLayer(layer, visible)')
    expect(prototypeHtml).toContain('data-dev-inspection="enclosures"')
    expect(prototypeHtml).not.toContain('data-dev-inspection="degree-one"')
    expect(prototypeHtml).not.toContain('显示一度端点复核')
    expect(css).toMatch(/\.enclosure-shape\s*\{[^}]*stroke-width:\s*1px;[^}]*vector-effect:\s*non-scaling-stroke/)
    expect(css).not.toContain('.degree-one-endpoint')
  })

  test('renders componentised doors and windows on the planar wall seam', () => {
    expect(openingCatalog.components).toHaveLength(9)
    expect(enclosureTopology.planarWalls).toHaveLength(enclosureTopology.planarEdgeCount)
    expect(enclosureTopology.planarWalls).toHaveLength(617)
    expect(source).toContain("import { createOpeningEditor } from './opening-editor.js'")
    expect(source).toContain('walls: enclosureTopology.planarWalls')
    expect(source).toContain('class="map-opening-system"')
    expect(source).toContain('class="opening-component ${placement.kind}${selectedClass}"')
    expect(source).toContain("['pan', 'snap', 'opening']")
    expect(prototypeHtml).toContain('data-dev-wall-mode="opening"')
    expect(prototypeHtml).toContain('data-dev-opening-component="door-double-large"')
    expect(prototypeHtml).toContain('data-dev-opening-component="window-interior-observation"')
    expect(prototypeHtml).toContain('data-dev-opening="copy"')
    expect(css).toContain('.hospital-map-prototype.opening-placement-mode .grid-intersection-hit')
  })

  test('loads the uploaded supply-centre openings as the confirmed baseline', () => {
    expect(baselineOpenings.schema).toBe('hospital-opening-layout/v1')
    expect(baselineOpenings._source).toEqual(['reference/供应中心门窗.json'])
    expect(baselineOpenings.placements).toHaveLength(86)
    expect(baselineOpenings.placements.filter(placement => placement.kind === 'door')).toHaveLength(51)
    expect(baselineOpenings.placements.filter(placement => placement.kind === 'window')).toHaveLength(35)
    expect(source).toContain("import baselineOpeningLayout from '../../../data/hospital_ref/floor-one-openings.json'")
    expect(source).toContain('openingEditor = createEditor(baselineOpeningLayout)')
    expect(prototypeHtml).toContain('恢复已上传基线')
  })

  test('keeps the two owner-confirmed large-double-door boundaries in the repaired topology', () => {
    expect(topologyRepairs.supplementalWalls).toEqual([
      { from: { x: -57700, y: 0 }, to: { x: -57700, y: -3000 }, futureOpening: 'large-double-door' },
      { from: { x: 82125, y: 0 }, to: { x: 84000, y: 0 }, futureOpening: 'large-double-door' },
    ])
    expect(enclosureTopology.sourceWallCount).toBe(364)
    expect(enclosureTopology.enclosures).toHaveLength(189)
  })

  test('uses a raster interaction cache and restores the vector plan when zoom settles', () => {
    const restingCameraRule = css.match(/^\.map-camera\s*\{[^}]*\}/m)?.[0] || ''
    expect(restingCameraRule).not.toContain('will-change')
    expect(source).toContain('map-plan-vector')
    expect(source).toContain('map-plan-preview')
    expect(source).toContain("host.classList.add('map-zooming')")
    expect(source).toContain("host.classList.remove('map-zooming')")
    expect(css).toMatch(/\.hospital-map-prototype\.map-zooming \.map-camera,[^}]*will-change:\s*transform/)
    expect(css).toMatch(/\.hospital-map-prototype\.map-zooming \.map-plan-vector,[^}]*visibility:\s*hidden/)
    expect(css).toMatch(/\.hospital-map-prototype\.map-zooming \.map-plan-preview,[^}]*visibility:\s*visible/)
  })

  test('coalesces wheel input into animation frames and preserves wheel magnitude', () => {
    expect(source).toContain('requestAnimationFrame(runWheelZoomFrame)')
    expect(zoomMotionSource).toMatch(/Math\.exp\([^)]*deltaY/)
    expect(source).not.toContain("event.deltaY < 0 ? .2 : -.2")
  })

  test('keeps the time filter on a persistent compositor layer during zoom', () => {
    expect(source).toContain('map-time-filter')
    expect(css).toMatch(/\.map-time-filter\s*\{[^}]*z-index:\s*10;[^}]*translateZ\(0\)/)
    expect(css).not.toContain('.hospital-map-prototype::after')
  })

  test('uses the same viewport time filter for vector and SVG-derived raster frames', () => {
    expect(source).toContain("cache/page-26-web.png?url")
    expect(source).not.toContain("full/page-26.png?url")
    expect(source).toContain('<img class="map-plan-preview"')
    expect(css).not.toMatch(/\.map-plan-preview\s*\{[^}]*(?:--time-wash|--time-edge)/)
    expect(css).not.toMatch(/\.hospital-map-prototype\.map-zooming \.map-time-filter\s*\{[^}]*visibility:\s*hidden/)
  })

  test('keeps the SVG-derived cache transparent and aligned to the reference dimensions', () => {
    // 来源：design/presentation/500床一层跑团地图原型.md §一、§四。
    expect(planPreviewPng.readUInt32BE(16)).toBe(4963)
    expect(planPreviewPng.readUInt32BE(20)).toBe(3509)
    expect(planPreviewPng[25]).toBe(6)
  })

  test('keeps only the aligned coordinate readout on the map surface', () => {
    expect(css).toMatch(/\.scene\.map-prototype-active \.scene-topbar,[\s\S]*\.scene\.map-prototype-active \.scene-bottom\s*\{\s*pointer-events:\s*none/)
    expect(source).toContain('map-coordinate-hud')
    expect(source).not.toContain('map-zoom-controls')
    expect(source).not.toContain('map-prototype-switcher')
    expect(css).toMatch(/\.map-coordinate-hud\s*\{[^}]*left:\s*50%;[^}]*grid-template-columns:/)
  })

})
