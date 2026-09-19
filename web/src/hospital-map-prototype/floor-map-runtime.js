// A small movement boundary: presentation adapters ask for a view and request moves;
// they do not own adjacency rules or mutate the map model.
export function createFloorMapRuntime(map, start = map.initialLocation) {
  const locations = new Map(map.locations.map(location => [location.id, location]))
  const neighbours = new Map(map.locations.map(location => [location.id, new Set()]))

  for (const [from, to] of map.connections) {
    if (!locations.has(from) || !locations.has(to)) throw new Error(`Unknown map connection: ${from} -> ${to}`)
    neighbours.get(from).add(to)
    neighbours.get(to).add(from)
  }
  if (!locations.has(start)) throw new Error(`Unknown initial location: ${start}`)

  let currentLocationId = start

  function view() {
    const reachable = neighbours.get(currentLocationId)
    return {
      currentLocation: locations.get(currentLocationId),
      locations: map.locations.map(location => ({
        ...location,
        current: location.id === currentLocationId,
        reachable: reachable.has(location.id),
      })),
      actors: map.actors.map(actor => ({ ...actor, coLocated: actor.location === currentLocationId })),
      connections: map.connections,
    }
  }

  function move(destinationId) {
    if (!locations.has(destinationId)) return { moved: false, reason: 'unknown-location', ...view() }
    if (destinationId === currentLocationId) return { moved: false, reason: 'already-there', ...view() }
    if (!neighbours.get(currentLocationId).has(destinationId)) return { moved: false, reason: 'not-adjacent', ...view() }
    currentLocationId = destinationId
    return { moved: true, reason: null, ...view() }
  }

  return { move, view }
}
