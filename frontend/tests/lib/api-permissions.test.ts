import { describe, expect, it } from "vitest"

import { lockedReads, permissionsByGroup, tick } from "@/lib/api-permissions"

// As the api service answers them.
const implied = {
  "interviews:create": "interviews:read",
  "candidates:invite": "candidates:read",
}
const groups = {
  interviews: ["interviews:read", "interviews:create"],
  candidates: ["candidates:read", "candidates:invite"],
  credits: ["credits:read"],
}

describe("tick", () => {
  it("adds the read a permission comes with", () => {
    expect(tick([], "candidates:invite", implied).sort()).toEqual([
      "candidates:invite",
      "candidates:read",
    ])
  })

  it("adds a permission without a read alone, and nothing twice", () => {
    expect(tick(["credits:read"], "credits:read", implied)).toEqual([
      "credits:read",
    ])
    expect(tick(["interviews:read"], "interviews:create", implied)).toEqual([
      "interviews:read",
      "interviews:create",
    ])
  })
})

describe("lockedReads", () => {
  it("locks the reads of the ticked permissions only", () => {
    expect(
      lockedReads(["candidates:invite", "interviews:read"], implied)
    ).toEqual(new Set(["candidates:read"]))
  })
})

describe("permissionsByGroup", () => {
  it("lists each group's ticked permissions in the groups' order, without empty groups", () => {
    expect(
      permissionsByGroup(
        ["candidates:invite", "interviews:read", "candidates:read"],
        groups
      )
    ).toEqual([
      { group: "interviews", permissions: ["interviews:read"] },
      {
        group: "candidates",
        permissions: ["candidates:read", "candidates:invite"],
      },
    ])
  })
})
