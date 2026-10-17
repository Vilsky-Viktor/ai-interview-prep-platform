import { describe, expect, it } from "vitest"

import { reversed, sourceWires } from "@/lib/source-wires"

const numbers = (d: string) => d.match(/-?[\d.]+/g)!.map(Number)
// Where a wire starts and where it ends.
const ends = (d: string) => {
  const all = numbers(d)

  return { from: all.slice(0, 2), to: all.slice(6, 8) }
}

// A card in the middle of the frame: 100 to 200 across, 100 to 160 down.
const CARD = { left: 100, top: 100, width: 100, height: 60 }

describe("sourceWires", () => {
  it("meets the near side of a card beside it, from inside the source's facing side", () => {
    const left = { left: 0, top: 110, width: 40, height: 40 }
    const right = { left: 260, top: 110, width: 40, height: 40 }
    const [fromLeft, fromRight] = sourceWires(CARD, [left, right], 10, 4)

    expect(ends(fromLeft)).toEqual({ from: [36, 130], to: [100, 130] })
    expect(ends(fromRight)).toEqual({ from: [264, 130], to: [200, 130] })
  })

  it("meets the top or bottom of a card above or below it", () => {
    const above = { left: 130, top: 0, width: 40, height: 40 }
    const below = { left: 130, top: 220, width: 40, height: 40 }
    const [fromAbove, fromBelow] = sourceWires(CARD, [above, below], 10, 4)

    expect(ends(fromAbove)).toEqual({ from: [150, 36], to: [150, 100] })
    expect(ends(fromBelow)).toEqual({ from: [150, 224], to: [150, 160] })
  })

  it("spaces wires on one side by the gap, in the sources' order, around the middle", () => {
    const top = { left: 0, top: 0, width: 40, height: 40 }
    const middle = { left: 0, top: 110, width: 40, height: 40 }
    const bottom = { left: 0, top: 220, width: 40, height: 40 }
    // Given out of order, they still meet the card in order, so no two cross.
    const wires = sourceWires(CARD, [bottom, top, middle], 12, 0)

    expect(wires.map((wire) => ends(wire).to[1])).toEqual([142, 118, 130])
  })

  it("leaves and meets straight on", () => {
    const [wire] = sourceWires(
      CARD,
      [{ left: 0, top: 0, width: 40, height: 40 }],
      10,
      0
    )
    const [x1, y1, ax, ay, bx, by, x2, y2] = numbers(wire)

    // Beside the card: level as it leaves the source and as it reaches the card.
    expect(ay).toBe(y1)
    expect(by).toBe(y2)
    expect(ax).toBe(bx)
    expect(x1).toBeLessThan(x2)
  })
})

describe("reversed", () => {
  it("draws the same curve from its other end", () => {
    expect(reversed("M 1 2 C 3 4, 5 6, 7 8")).toBe("M 7 8 C 5 6, 3 4, 1 2")
  })

  it("keeps negative and fractional numbers", () => {
    expect(reversed("M -1.5 2 C 3 -4.25, 5 6, 7 8")).toBe(
      "M 7 8 C 5 6, 3 -4.25, -1.5 2"
    )
  })
})
