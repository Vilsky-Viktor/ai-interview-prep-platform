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
      // On the host the page was opened from, so a phone on the same network reaches it too.
      const url = new URL(emulatorUrl)
      url.hostname = window.location.hostname
      connectAuthEmulator(auth, url.origin, { disableWarnings: true })
    }

    return auth
  })

  return loading
}
