"use client"

import { useRouter } from "next/navigation"
import { useState } from "react"
import { toast } from "sonner"

import { useAuth } from "@/components/auth-provider"
import { Button } from "@/components/ui/button"
import { signIn } from "@/lib/auth"
import { openCheckout } from "@/lib/paddle"
import type { Catalog, Product } from "@/types/billing"

/** Buys one product for the signed-in user, or for `companyId` when given. */
export function BuyButton({
  catalog,
  product,
  companyId,
  label = "Buy",
  variant = "default",
}: {
  catalog: Catalog
  product: Product
  companyId?: string
  label?: string
  variant?: "default" | "outline"
}) {
  const router = useRouter()
  const { user } = useAuth()
  const [opening, setOpening] = useState(false)

  if (!product.price_id) {
    return (
      <Button variant="outline" className="h-12 px-6 text-base" disabled>
        Coming soon
      </Button>
    )
  }

  async function buy() {
    if (!user) {
      await signIn()

      return
    }

    setOpening(true)

    try {
      await openCheckout(
        catalog,
        product.price_id!,
        companyId
          ? { owner_type: "company", owner_id: companyId, buyer_id: user.uid }
          : { owner_type: "user", owner_id: user.uid, buyer_id: user.uid },
        user.email,
        () => {
          toast.success("Payment received. It shows up here in a moment.")
          // The webhook usually lands within seconds; show the new balance then.
          window.setTimeout(() => router.refresh(), 4000)
        }
      )
    } catch {
      toast.error("Couldn't open the checkout. Please try again.")
    } finally {
      setOpening(false)
    }
  }

  return (
    <Button
      variant={variant}
      className="h-12 px-6 text-base"
      disabled={opening}
      onClick={buy}
    >
      {label}
    </Button>
  )
}
