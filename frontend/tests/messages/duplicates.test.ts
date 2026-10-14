import { describe, expect, it } from "vitest"

import { duplicateKeys } from "../../scripts/duplicate-keys.mjs"

// JSON.parse keeps the last of two equal keys silently, so a new message can replace an old
// one with the same name; the check reads the raw text instead.
describe("duplicateKeys", () => {
  it("finds a key written twice in one object", () => {
    expect(duplicateKeys('{"a": {"x": "1", "x": "2"}, "b": "3"}')).toEqual([
      "x",
    ])
  })

  it("lets the same key appear in different objects and lists stay values", () => {
    expect(
      duplicateKeys(
        '{"a": {"x": "1"}, "b": {"x": "2"}, "c": ["x", "x"], "d": "say \\"x\\""}'
      )
    ).toEqual([])
  })
})
