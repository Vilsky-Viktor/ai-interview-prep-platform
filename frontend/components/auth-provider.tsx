"use client"

import * as Sentry from "@sentry/nextjs"
import { onIdTokenChanged } from "firebase/auth"
import { useRouter } from "next/navigation"
import { createContext, useContext, useEffect, useState } from "react"

import { apiFetch } from "@/lib/api"
import { readTokenCookie, writeTokenCookie } from "@/lib/auth"
import { auth } from "@/lib/firebase"
import { isLocale, readLocaleCookie, writeLocaleCookie } from "@/lib/locale"
import type { AuthState } from "@/types/auth"

const AuthContext = createContext<AuthState>({ user: null, loading: true })

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter()
  const [state, setState] = useState<AuthState>({ user: null, loading: true })

  useEffect(() => {
    return onIdTokenChanged(auth, async (user) => {
      const token = user ? await user.getIdToken() : null
      // Firebase reports the restored session on every page load; the pages were already
      // rendered with that token, so they re-render only when the token or language changes.
      let changed = token !== readTokenCookie()

      if (changed) {
        writeTokenCookie(token)
      }

      // The interface follows the account's language, also on a new device.
      if (user) {
        const { claims } = await user.getIdTokenResult()
        const language = String(claims.language ?? "")

        if (isLocale(language) && language !== readLocaleCookie()) {
          writeLocaleCookie(language)
          changed = true
        }

        // A new account keeps the language it signed up in, for the interface and its emails.
        // The refreshed token carries it, and this runs again with it.
        if (!claims.language && isLocale(document.documentElement.lang)) {
          await apiFetch("/library/me/settings", {
            method: "PUT",
            body: JSON.stringify({ language: document.documentElement.lang }),
          })
            .then(() => user.getIdToken(true))
            .catch(() => {})
        }
      }

      // Errors name the account by id only, never by email.
      Sentry.setUser(user ? { id: user.uid } : null)
      setState({ user, loading: false })
      // Server-rendered pages read the token cookie, so re-render them with the new one.
      if (changed) {
        router.refresh()
      }
    })
  }, [router])

  return <AuthContext value={state}>{children}</AuthContext>
}

export function useAuth() {
  return useContext(AuthContext)
}
