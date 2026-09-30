import { FirebaseError } from "firebase/app"
import {
  GoogleAuthProvider,
  signInWithPopup,
  signOut as firebaseSignOut,
} from "firebase/auth"
import { toast } from "sonner"

import {
  POPUP_CLOSED_CODES,
  TOKEN_COOKIE,
  TOKEN_COOKIE_MAX_AGE,
} from "@/constants/auth"
import { auth } from "@/lib/firebase"

export async function signIn() {
  try {
    await signInWithPopup(auth, new GoogleAuthProvider())
  } catch (error) {
    if (
      error instanceof FirebaseError &&
      POPUP_CLOSED_CODES.includes(error.code)
    ) {
      return
    }

    toast.error("Sign-in failed. Please try again.")
  }
}

export function signOut() {
  return firebaseSignOut(auth)
}

export function writeTokenCookie(token: string | null) {
  const maxAge = token ? TOKEN_COOKIE_MAX_AGE : 0
  const secure = location.protocol === "https:" ? "; secure" : ""
  document.cookie = `${TOKEN_COOKIE}=${token ?? ""}; path=/; max-age=${maxAge}; samesite=lax${secure}`
}
