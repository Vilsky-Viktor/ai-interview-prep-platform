import { expect, it, vi } from "vitest"

const getAuth = vi.fn(() => ({ name: "auth" }))
const connectAuthEmulator = vi.fn()

vi.mock("firebase/app", () => ({ initializeApp: vi.fn(() => ({})) }))
vi.mock("firebase/auth", () => ({ getAuth, connectAuthEmulator }))

it("loads Firebase Auth once, on first use, against the emulator when set", async () => {
  vi.stubEnv("NEXT_PUBLIC_FIREBASE_AUTH_EMULATOR_URL", "http://localhost:9099")
  const { firebaseAuth } = await import("@/lib/firebase")

  expect(getAuth).not.toHaveBeenCalled()
  const [first, second] = await Promise.all([firebaseAuth(), firebaseAuth()])

  expect(first).toBe(second)
  expect(await firebaseAuth()).toBe(first)
  expect(getAuth).toHaveBeenCalledTimes(1)
  expect(connectAuthEmulator).toHaveBeenCalledWith(
    first,
    "http://localhost:9099",
    { disableWarnings: true }
  )
})
