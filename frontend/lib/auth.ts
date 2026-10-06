import { FirebaseError } from "firebase/app"
import {
  type AuthCredential,
  type AuthProvider,
  GithubAuthProvider,
  GoogleAuthProvider,
  linkWithCredential,
  OAuthProvider,
  sendEmailVerification,
  signInWithPopup,
  signOut as firebaseSignOut,
} from "firebase/auth"

import {
  ACCOUNT_EXISTS,
  LINKEDIN_PROVIDER_ID,
  POPUP_CLOSED_CODES,
  TOKEN_COOKIE,
  TOKEN_COOKIE_MAX_AGE,
} from "@/constants/auth"
import { auth } from "@/lib/firebase"
import type { SignInProvider, SignInResult } from "@/types/sign-in"

// A way of signing in that met an existing account with the same email, waiting to be linked
// once its owner signs in the way they did before.
let pending: { credential: AuthCredential; email: string } | null = null

function providerFor(name: SignInProvider): AuthProvider {
  if (name === "github") {
    const github = new GithubAuthProvider()
    github.addScope("user:email")

    return github
  }

  if (name === "linkedin") {
    const linkedin = new OAuthProvider(LINKEDIN_PROVIDER_ID)
    linkedin.addScope("openid")
    linkedin.addScope("profile")
    linkedin.addScope("email")

    return linkedin
  }

  return new GoogleAuthProvider()
}

function credentialFrom(name: SignInProvider, error: FirebaseError) {
  if (name === "github") {
    return GithubAuthProvider.credentialFromError(error)
  }

  if (name === "linkedin") {
    return OAuthProvider.credentialFromError(error)
  }

  return GoogleAuthProvider.credentialFromError(error)
}

/** Signs in with one of the ways offered. One account per email: when the email already has
 * one under another way, this way is kept and linked once the person signs in as before. */
export async function signIn(name: SignInProvider): Promise<SignInResult> {
  try {
    const { user } = await signInWithPopup(auth, providerFor(name))

    if (pending && pending.email === user.email) {
      await linkWithCredential(user, pending.credential).catch(() => {})
    }

    pending = null

    // Invites need a verified email; some ways of signing in (GitHub) don't verify it, so a
    // link is sent to confirm it.
    if (!user.emailVerified) {
      await sendEmailVerification(user).catch(() => {})

      return "verify"
    }

    return "done"
  } catch (error) {
    if (!(error instanceof FirebaseError)) {
      return "failed"
    }

    if (POPUP_CLOSED_CODES.includes(error.code)) {
      return "cancelled"
    }

    const credential = credentialFrom(name, error)
    const email = (error.customData?.email as string | undefined) ?? null

    if (error.code === ACCOUNT_EXISTS && credential && email) {
      pending = { credential, email }

      return "link"
    }

    return "failed"
  }
}

export function signOut() {
  return firebaseSignOut(auth)
}

export function readTokenCookie() {
  return (
    document.cookie
      .split("; ")
      .find((item) => item.startsWith(`${TOKEN_COOKIE}=`))
      ?.split("=")[1] || null
  )
}

export function writeTokenCookie(token: string | null) {
  const maxAge = token ? TOKEN_COOKIE_MAX_AGE : 0
  const secure = location.protocol === "https:" ? "; secure" : ""
  document.cookie = `${TOKEN_COOKIE}=${token ?? ""}; path=/; max-age=${maxAge}; samesite=lax${secure}`
}
