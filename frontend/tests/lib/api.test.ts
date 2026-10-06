import { describe, expect, it, vi } from "vitest"

import { errorDetail } from "@/lib/api"

vi.mock("@/lib/firebase", () => ({ auth: {} }))

describe("errorDetail", () => {
  it("takes the message a service raised", () => {
    expect(errorDetail({ detail: "Company not found" })).toBe(
      "Company not found"
    )
  })

  it("takes the first validation error, without pydantic's prefix", () => {
    const body = {
      detail: [
        { msg: "Value error, Too many emails" },
        { msg: "Field required" },
      ],
    }

    expect(errorDetail(body)).toBe("Too many emails")
  })

  it("gives none for any other body", () => {
    expect(errorDetail(null)).toBeNull()
    expect(errorDetail({})).toBeNull()
    expect(errorDetail({ detail: [] })).toBeNull()
    expect(errorDetail({ detail: [{ loc: ["body"] }] })).toBeNull()
    expect(errorDetail({ detail: 42 })).toBeNull()
  })
})
