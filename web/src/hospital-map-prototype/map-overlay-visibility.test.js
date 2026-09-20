import { describe, expect, test } from 'bun:test'
import { readFileSync } from 'node:fs'
import { floorOneMap } from './floor-one-map.js'

const css = readFileSync(new URL('./hospital-map-prototype.css', import.meta.url), 'utf8')
const source = readFileSync(new URL('./hospital-map-prototype.js', import.meta.url), 'utf8')
const zoomMotionSource = readFileSync(new URL('./zoom-motion.js', import.meta.url), 'utf8')
const prototypeHtml = readFileSync(new URL('../../../design/presentation/叙事界面原型.html', import.meta.url), 'utf8')
const planPreviewPng = readFileSync(new URL('../../../data/hospital_ref/cache/page-26-web.png', import.meta.url))

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
    expect(overlayCount).toBeGreaterThanOrEqual(3)
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

  test('places calibrated activities inside the nearby authored rooms, not on the search anchors', () => {
    const visitingPhone = floorOneMap.locations.find(location => location.id === 'phone_bay')
    const nurseStation = floorOneMap.locations.find(location => location.id === 'nurse_station')
    expect(visitingPhone).toMatchObject({ name: '探视房电话', x: 76, y: 61.9 })
    expect(nurseStation).toMatchObject({ name: '南病房护士站', x: 58, y: 60.8 })
    expect(visitingPhone.region).not.toContain('73.7659')
    expect(nurseStation.region).not.toContain('55.3194')
  })

  test('uses corrected cardinal regions and removes the old screen-relative locations', () => {
    const ids = floorOneMap.locations.map(location => location.id)
    for (const id of ['north_ward', 'south_ward', 'basketball_court', 'south_courtyard']) expect(ids).toContain(id)
    for (const id of ['east_ward', 'west_ward', 'courtyard', 'garden']) expect(ids).not.toContain(id)
    expect(floorOneMap.locations.find(location => location.id === 'basketball_court')).toMatchObject({ name: '中央篮球活动场', x: 46.4 })
    expect(floorOneMap.actors.find(actor => actor.id === 'wu_tong').schedule.morning.location).toBe('north_ward')
    expect(floorOneMap.actors.find(actor => actor.id === 'zhou_weiguo').schedule.morning.location).toBe('south_ward')
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

  test('rotates the plan, NPC points, and their names as one map layer', () => {
    expect(css).toMatch(/\.map-plan-stage, \.tabletop-board, \.route-network\s*\{[^}]*transform:\s*rotate\(var\(--map-rotation/)
    expect(css).toMatch(/\.map-person b\s*\{[^}]*width:\s*10px;[^}]*height:\s*10px/)
    expect(source).toContain("location.y - 1")
  })

  test('shows the current known NPC name only on hover or keyboard focus', () => {
    expect(css).toMatch(/\.map-person span\s*\{[^}]*opacity:\s*0;[^}]*visibility:\s*hidden/)
    expect(css).toMatch(/\.map-person:hover span,[\s\S]*\.map-person:focus-visible span\s*\{[^}]*opacity:\s*1;[^}]*visibility:\s*visible/)
    expect(source).toContain('getNpcDossier')
  })
})
