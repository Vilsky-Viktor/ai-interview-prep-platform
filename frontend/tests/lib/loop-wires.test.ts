import { describe, expect, it } from "vitest"

import { loopWires } from "@/lib/loop-wires"

const numbers = (d: string) => d.match(/-?[\d.]+/g)!.map(Number)

// A square's corners, clockwise.
const SQUARE = [
  { x: 0, y: 0 },
  { x: 60, y: 0 },
  { x: 60, y: 60 },
  { x: 0, y: 60 },
]

describe("loopWires", () => {
  it("draws a curve from each point to the next, the last back to the first", () => {
    const wires = loopWires(SQUARE)

    expect(wires).toHaveLength(4)
    wires.forEach((wire, index) => {
      const [x1, y1, , , , , x2, y2] = numbers(wire)
      const to = SQUARE[(index + 1) % SQUARE.length]

      expect([x1, y1]).toEqual([SQUARE[index].x, SQUARE[index].y])
      expect([x2, y2]).toEqual([to.x, to.y])
    })
  })

  it("leaves each point along the line between its neighbours", () => {
    // From (60, 0): its neighbours are (0, 0) and (60, 60), a sixth of the way between them.
    expect(loopWires(SQUARE)[1]).toBe("M 60 0 C 70 10, 70 50, 60 60")
  })

  it("joins the curves without a corner", () => {
    const wires = loopWires(SQUARE).map(numbers)

    wires.forEach((wire, index) => {
      const next = wires[(index + 1) % wires.length]
      // The arriving handle, the point and the leaving handle lie on one line.
      const [bx, by, x, y] = wire.slice(4)
      const [ax, ay] = next.slice(2, 4)

      expect((x - bx) * (ay - y) - (y - by) * (ax - x)).toBeCloseTo(0)
    })
  })
})
