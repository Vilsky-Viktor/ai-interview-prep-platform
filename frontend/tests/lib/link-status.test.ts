import { describe, expect, it } from "vitest"

import { ApiError } from "@/lib/api"
import { linkFailure } from "@/lib/link-status"

describe("linkFailure", () => {
  it("calls a link invalid only when the API says it's gone", () => {
    expect(linkFailure(new ApiError(404, "Invite not found"))).toBe("missing")
    expect(linkFailure(new ApiError(410, "Gone"))).toBe("missing")
  })

  it("lets anything else be tried again", () => {
    for (const status of [429, 500, 502, 503]) {
      expect(linkFailure(new ApiError(status, "Busy"))).toBe("failed")
    }

    expect(linkFailure(new TypeError("Failed to fetch"))).toBe("failed")
  })
})
