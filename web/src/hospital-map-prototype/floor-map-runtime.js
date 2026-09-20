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

  function actorsAt(time) {
    return map.actors.flatMap(actor => {
      if (!actor.schedule) return [{ ...actor }]
      const situation = actor.schedule[time]
      return situation ? [{ ...actor, ...situation }] : []
    })
  }

  function view(time = 'morning') {
    const reachable = neighbours.get(currentLocationId)
    return {
      currentLocation: locations.get(currentLocationId),
      locations: map.locations.map(location => ({
        ...location,
        current: location.id === currentLocationId,
        reachable: reachable.has(location.id),
      })),
      actors: actorsAt(time).map(actor => ({ ...actor, coLocated: actor.location === currentLocationId })),
      connections: map.connections,
    }
  }

  function move(destinationId, time = 'morning') {
    if (!locations.has(destinationId)) return { moved: false, reason: 'unknown-location', ...view(time) }
    if (destinationId === currentLocationId) return { moved: false, reason: 'already-there', ...view(time) }
    if (!neighbours.get(currentLocationId).has(destinationId)) return { moved: false, reason: 'not-adjacent', ...view(time) }
    currentLocationId = destinationId
    return { moved: true, reason: null, ...view(time) }
  }

  return { move, view }
}
