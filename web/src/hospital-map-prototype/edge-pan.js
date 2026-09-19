// 来源：design/presentation/500床一层跑团地图原型.md §一·校图坐标系。
export const EDGE_PAN_ZONE_PIXELS = 48
export const EDGE_PAN_MAX_SPEED = 720
export const EDGE_PAN_MAX_FRAME_SECONDS = .05

export function edgePanVelocity(position, start, end) {
  if (position < start || position > end) return 0
  const fromStart = position - start
  if (fromStart < EDGE_PAN_ZONE_PIXELS) {
    return -EDGE_PAN_MAX_SPEED * (1 - fromStart / EDGE_PAN_ZONE_PIXELS)
  }
  const fromEnd = end - position
  if (fromEnd < EDGE_PAN_ZONE_PIXELS) {
    return EDGE_PAN_MAX_SPEED * (1 - fromEnd / EDGE_PAN_ZONE_PIXELS)
  }
  return 0
}
