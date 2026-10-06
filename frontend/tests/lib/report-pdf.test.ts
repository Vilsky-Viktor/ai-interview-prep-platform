import { describe, expect, it } from "vitest"

import { pageSlices } from "@/lib/report-pdf"

// Where the report's top is on screen: slices are measured from it.
const TOP = 100

/** A laid-out report whose blocks and rows span these px ranges from its top. */
function report(rows: [number, number][], height: number) {
  const boxes = rows.map(([top, bottom]) => ({
    getBoundingClientRect: () => ({ top: TOP + top, bottom: TOP + bottom }),
  }))

  return {
    getBoundingClientRect: () => ({ top: TOP }),
    querySelectorAll: () => boxes,
    offsetHeight: height,
  } as unknown as HTMLElement
}

describe("pageSlices", () => {
  it("keeps a short report on one page", () => {
    const node = report(
      [
        [0, 100],
        [100, 300],
      ],
      320
    )

    expect(pageSlices(node, 500)).toEqual([{ start: 0, height: 320 }])
  })

  // A 500px page: the first keeps 447px (one 53px margin), the others 394px (two).
  it("ends each page before the first row that wouldn't fit", () => {
    const node = report(
      [
        [0, 200],
        [200, 440],
        [440, 600],
        [600, 830],
        [830, 1000],
      ],
      1000
    )

    expect(pageSlices(node, 500)).toEqual([
      { start: 0, height: 440 },
      { start: 440, height: 390 },
      { start: 830, height: 170 },
    ])
  })

  it("breaks before a row that ends just past the first page's room", () => {
    const node = report(
      [
        [0, 447],
        [447, 448],
      ],
      448
    )

    expect(pageSlices(node, 500)).toEqual([
      { start: 0, height: 447 },
      { start: 447, height: 1 },
    ])
  })
})
