import { describe, expect, it, vi } from "vitest"

const sendEmailVerification = vi.hoisted(() => vi.fn())
const user = vi.hoisted(() => ({
  email: "ann@example.com",
  emailVerified: false,
}))

vi.mock("@/lib/firebase", () => ({ firebaseAuth: async () => ({}) }))
vi.mock("firebase/auth", () => ({
  GithubAuthProvider: class {
    addScope() {}
  },
  signInWithPopup: async () => ({ user }),
  sendEmailVerification,
}))

import { signIn } from "@/lib/auth"

describe("signIn with an unverified email", () => {
  it("says the link to verify it was sent", async () => {
    sendEmailVerification.mockResolvedValueOnce(undefined)

    expect(await signIn("github")).toBe("verify")
  })

  it("says so when the link couldn't be sent", async () => {
    sendEmailVerification.mockRejectedValueOnce(
      new Error("auth/too-many-requests")
    )

    expect(await signIn("github")).toBe("verifyFailed")
  })
})
