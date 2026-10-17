import { afterEach, describe, expect, it, vi } from "vitest"

import { pageContext } from "@/lib/page-context"
import { pageKey, registerPageKey } from "@/lib/page-key"

const COMPANY = "8c1d2b8e-1a2b-4c3d-8e9f-0a1b2c3d4e5f"
const INTERVIEW = "1f2e3d4c-5b6a-4978-8a9b-0c1d2e3f4a5b"

function on(search: string) {
  vi.stubGlobal("window", { location: { search } })
}

afterEach(() => {
  vi.unstubAllGlobals()
})

describe("page context", () => {
  it("sends the page's key, its path with the tab and the ids its route names", () => {
    on("?tab=candidates")
    const path = `/companies/${COMPANY}/interviews/${INTERVIEW}`

    expect(
      pageContext(
        "interviewCandidates",
        { companyId: COMPANY, id: INTERVIEW },
        path
      )
    ).toEqual({
      key: "interviewCandidates",
      path: `${path}?tab=candidates`,
      company_id: COMPANY,
      interview_id: INTERVIEW,
      candidate_id: undefined,
      template_id: undefined,
      practice_round_id: undefined,
    })
  })

  it("names no interview for an id outside a company's pages", () => {
    on("")

    expect(
      pageContext("practiceTest", { id: "t1" }, "/practice/t1")
    ).toMatchObject({
      key: "practiceTest",
      path: "/practice/t1",
      interview_id: undefined,
    })
  })

  it("sends nothing on a page without a key, like the admin zone", () => {
    on("")

    expect(
      pageContext(null, { id: "c1" }, "/superadmin/companies/c1")
    ).toBeNull()
  })
})

describe("page key", () => {
  it("is the page on screen until it goes, and a newer page keeps its own", () => {
    const leaveBilling = registerPageKey("billing")
    expect(pageKey()).toBe("billing")

    const leaveSettings = registerPageKey("settings")
    leaveBilling()
    expect(pageKey()).toBe("settings")

    leaveSettings()
    expect(pageKey()).toBeNull()
  })
})
