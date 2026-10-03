"use client"

import * as Sentry from "@sentry/nextjs"
import { onIdTokenChanged } from "firebase/auth"
import { useRouter } from "next/navigation"
import { createContext, useContext, useEffect, useState } from "react"

import { DEFAULT_LOCALE } from "@/constants/i18n"
import { writeTokenCookie } from "@/lib/auth"
import { auth } from "@/lib/firebase"
import { isLocale, readLocaleCookie, writeLocaleCookie } from "@/lib/locale"
import type { AuthState } from "@/types/auth"

const AuthContext = createContext<AuthState>({ user: null, loading: true })

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter()
  const [state, setState] = useState<AuthState>({ user: null, loading: true })

  useEffect(() => {
    return onIdTokenChanged(auth, async (user) => {
      writeTokenCookie(user ? await user.getIdToken() : null)

      // The interface follows the account's language, also on a new device.
      if (user) {
        const { claims } = await user.getIdTokenResult()
        const language = String(claims.language ?? DEFAULT_LOCALE)

        if (isLocale(language) && language !== readLocaleCookie()) {
          writeLocaleCookie(language)
        }
      }

      // Errors name the account by id only, never by email.
      Sentry.setUser(user ? { id: user.uid } : null)
      setState({ user, loading: false })
      // Server-rendered pages read the token cookie, so re-render them with the new one.
      router.refresh()
    })
  }, [router])

  return <AuthContext value={state}>{children}</AuthContext>
}

export function useAuth() {
  return useContext(AuthContext)
}
