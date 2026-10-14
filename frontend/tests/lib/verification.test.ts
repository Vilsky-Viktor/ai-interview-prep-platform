import { describe, expect, it, vi } from "vitest"

const auth = vi.hoisted(() => ({ currentUser: null as unknown }))

vi.mock("@/lib/firebase", () => ({ firebaseAuth: async () => auth }))

import { refreshVerification } from "@/lib/auth"

function account(verifiedOnReload: boolean) {
  const user = {
    emailVerified: false,
    reload: vi.fn(async () => {
      user.emailVerified = verifiedOnReload
    }),
    getIdToken: vi.fn(async () => "token"),
  }

  return user
}

describe("refreshVerification", () => {
  it("takes an email verified in another tab, with a new token saying so", async () => {
    const user = account(true)
    auth.currentUser = user

    await refreshVerification()

    expect(user.reload).toHaveBeenCalled()
    expect(user.getIdToken).toHaveBeenCalledWith(true)
  })

  it("asks for no new token while the email isn't verified", async () => {
    const user = account(false)
    auth.currentUser = user

    await refreshVerification()

    expect(user.getIdToken).not.toHaveBeenCalled()
  })

  it("leaves a verified account alone", async () => {
    const user = { ...account(true), emailVerified: true }
    auth.currentUser = user

    await refreshVerification()

    expect(user.reload).not.toHaveBeenCalled()
  })
})
