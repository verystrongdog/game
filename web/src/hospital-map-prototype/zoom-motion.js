// 来源：design/presentation/500床一层跑团地图原型.md §四（Web 原型缩放手感参数）。
export const MIN_ZOOM = .65
export const MAX_ZOOM = 64
export const WHEEL_ZOOM_RATE = .0032
export const WHEEL_ZOOM_EASING = .42
export const WHEEL_ZOOM_SETTLE = .002

export function clampZoom(zoom) {
  return Math.min(MAX_ZOOM, Math.max(MIN_ZOOM, zoom))
}

export function wheelZoomTarget(currentZoom, deltaY) {
  return clampZoom(currentZoom * Math.exp(-deltaY * WHEEL_ZOOM_RATE))
}

export function nextWheelZoom(currentZoom, targetZoom) {
  if (Math.abs(targetZoom - currentZoom) < WHEEL_ZOOM_SETTLE) return targetZoom
  return currentZoom + (targetZoom - currentZoom) * WHEEL_ZOOM_EASING
}
