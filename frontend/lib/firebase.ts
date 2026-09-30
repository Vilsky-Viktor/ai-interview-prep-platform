import { initializeApp } from "firebase/app"
import { connectAuthEmulator, getAuth } from "firebase/auth"

const app = initializeApp({
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
})

export const auth = getAuth(app)

const emulatorUrl = process.env.NEXT_PUBLIC_FIREBASE_AUTH_EMULATOR_URL

if (emulatorUrl) {
  connectAuthEmulator(auth, emulatorUrl, { disableWarnings: true })
}
