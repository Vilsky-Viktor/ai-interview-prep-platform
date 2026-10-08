import type { Auth } from "firebase/auth"

let loading: Promise<Auth> | undefined

/** Firebase Auth, loaded on first use rather than with every page: auth-provider.tsx asks for
 * it once the page is up, so it's ready before anyone clicks to sign in. */
export function firebaseAuth() {
  loading ??= Promise.all([
    import("firebase/app"),
    import("firebase/auth"),
  ]).then(([{ initializeApp }, { connectAuthEmulator, getAuth }]) => {
    const auth = getAuth(
      initializeApp({
        apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
        authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
        projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
      })
    )
    const emulatorUrl = process.env.NEXT_PUBLIC_FIREBASE_AUTH_EMULATOR_URL

    if (emulatorUrl) {
      connectAuthEmulator(auth, emulatorUrl, { disableWarnings: true })
    }

    return auth
  })

  return loading
}
