export function boxesOverlap(a, b, clearance = 0.04) {
  return a.min.x < b.max.x - clearance && a.max.x > b.min.x + clearance
    && a.min.z < b.max.z - clearance && a.max.z > b.min.z + clearance
    && a.min.y < b.max.y - clearance && a.max.y > b.min.y + clearance
}
