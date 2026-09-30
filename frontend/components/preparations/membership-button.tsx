"use client"

import { useRouter } from "next/navigation"
import { useState } from "react"
import { toast } from "sonner"

import { useAuth } from "@/components/auth-provider"
import { Button } from "@/components/ui/button"
import { apiFetch } from "@/lib/api"
import { signIn } from "@/lib/auth"
import type { PreparationSummary } from "@/types/preparation"

export function MembershipButton({
  preparation,
  joined,
}: {
  preparation: PreparationSummary
  joined: boolean
}) {
  const router = useRouter()
  const { user } = useAuth()
  const [busy, setBusy] = useState(false)

  async function toggle() {
    setBusy(true)

    try {
      await apiFetch(`/library/preparations/${preparation.id}/join`, {
        method: joined ? "DELETE" : "POST",
      })

      if (joined && preparation.visibility === "private") {
        // A shared private preparation is gone for this user after leaving.
        router.push("/preparations")

        return
      }

      router.refresh()
    } catch {
      toast.error("Something went wrong. Please try again.")
    } finally {
      setBusy(false)
    }
  }

  if (!user) {
    return <Button onClick={() => signIn()}>Sign in to join</Button>
  }

  return (
    <Button
      variant={joined ? "outline" : "default"}
      disabled={busy}
      onClick={toggle}
    >
      {joined ? "Leave" : "Join to practice"}
    </Button>
  )
}
