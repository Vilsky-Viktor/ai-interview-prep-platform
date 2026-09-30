"use client"

import { onIdTokenChanged } from "firebase/auth"
import { useRouter } from "next/navigation"
import { createContext, useContext, useEffect, useState } from "react"

import { writeTokenCookie } from "@/lib/auth"
import { auth } from "@/lib/firebase"
import type { AuthState } from "@/types/auth"

const AuthContext = createContext<AuthState>({ user: null, loading: true })

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter()
  const [state, setState] = useState<AuthState>({ user: null, loading: true })

  useEffect(() => {
    return onIdTokenChanged(auth, async (user) => {
      writeTokenCookie(user ? await user.getIdToken() : null)
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
