import { beforeEach, describe, expect, it, vi } from "vitest"

import { apiFetch } from "@/lib/api"
import {
  allOptionalEmailsOff,
  findAddress,
  saveForUser,
  setCompanyEmails,
} from "@/lib/superadmin-emails"

vi.mock("@/lib/api", () => ({ apiFetch: vi.fn(async () => ({})) }))

beforeEach(() => vi.mocked(apiFetch).mockClear())

describe("findAddress", () => {
  it("asks library and notifications with the address in the body", async () => {
    await findAddress("ann@example.com")

    const body = JSON.stringify({ email: "ann@example.com" })
    expect(apiFetch).toHaveBeenCalledWith("/library/superadmin/emails/lookup", {
      method: "POST",
      body,
    })
    expect(apiFetch).toHaveBeenCalledWith(
      "/notifications/superadmin/candidate-opt-outs/lookup",
      { method: "POST", body }
    )
  })
})

describe("allOptionalEmailsOff", () => {
  it("turns off every setting the Settings page shows", () => {
    expect(allOptionalEmailsOff()).toEqual({
      candidate_finished: false,
      invite_undelivered: false,
      ats_not_invited: false,
      interview_ready: false,
      reminders: false,
      updates: false,
      promotions: false,
    })
  })
})

describe("saveForUser", () => {
  it("saves the user's changes through the superadmin route", async () => {
    await saveForUser("u1", { updates: false })

    expect(apiFetch).toHaveBeenCalledWith(
      "/library/superadmin/emails/u1/preferences",
      { method: "PUT", body: JSON.stringify({ changes: { updates: false } }) }
    )
  })
})

describe("setCompanyEmails", () => {
  it("stops or lets through one company's emails to the address", async () => {
    await setCompanyEmails("ann@example.com", "c1", true)

    expect(apiFetch).toHaveBeenCalledWith(
      "/notifications/superadmin/candidate-opt-outs",
      {
        method: "PUT",
        body: JSON.stringify({
          email: "ann@example.com",
          company_id: "c1",
          stopped: true,
        }),
      }
    )
  })
})
