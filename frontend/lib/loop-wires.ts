type Point = { x: number; y: number }

/** The wires of a closed loop through `points` (in order, the last back to the first), one SVG
 * curve from each point to the next, together one smooth ring. */
export function loopWires(points: Point[]) {
  const at = (index: number) => points[(index + points.length) % points.length]

  return points.map((from, index) => {
    const before = at(index - 1)
    const to = at(index + 1)
    const after = at(index + 2)
    // Each end leaves along the line between its neighbours, so the ring has no corners.
    const ax = from.x + (to.x - before.x) / 6
    const ay = from.y + (to.y - before.y) / 6
    const bx = to.x - (after.x - from.x) / 6
    const by = to.y - (after.y - from.y) / 6

    return `M ${from.x} ${from.y} C ${ax} ${ay}, ${bx} ${by}, ${to.x} ${to.y}`
  })
}
