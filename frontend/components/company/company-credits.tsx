"use client"

import { useState } from "react"

import { BuyButton } from "@/components/billing/buy-button"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { formatPrice } from "@/lib/format"
import type { Catalog } from "@/types/billing"

/** How many candidates the company can still invite, and a way to buy more. */
export function CompanyCredits({
  companyId,
  credits,
  catalog,
}: {
  companyId: string
  credits: number
  catalog: Catalog
}) {
  const [open, setOpen] = useState(false)
  const packs = catalog.products.filter(
    (product) => product.owner === "company"
  )

  return (
    <div className="flex flex-wrap items-center justify-between gap-4 rounded-2xl border px-6 py-4">
      <p className="text-base">
        <span className="font-heading text-2xl font-medium tabular-nums">
          {credits}
        </span>{" "}
        <span className="text-muted-foreground">
          {credits === 1 ? "candidate" : "candidates"} left to invite
        </span>
      </p>
      <Button
        variant="outline"
        className="h-12 px-6 text-base"
        onClick={() => setOpen(true)}
      >
        Buy candidates
      </Button>
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent showCloseButton={false} className="sm:max-w-lg">
          <DialogHeader>
            <DialogTitle>Buy candidates</DialogTitle>
            <DialogDescription className="text-base">
              Each new candidate you invite uses one. Resending an invite is
              free, and credits never expire.
            </DialogDescription>
          </DialogHeader>
          <div className="divide-y rounded-xl border">
            {packs.map((pack) => (
              <div
                key={pack.key}
                className="flex items-center justify-between gap-4 px-5 py-4"
              >
                <span className="space-y-1">
                  <span className="block text-lg font-medium">
                    {pack.title}
                  </span>
                  <span className="block text-sm text-muted-foreground">
                    {formatPrice(pack.price_cents, catalog.currency)} ·{" "}
                    {formatPrice(
                      pack.price_cents / pack.candidate_credits,
                      catalog.currency
                    )}{" "}
                    each
                  </span>
                </span>
                <BuyButton
                  catalog={catalog}
                  product={pack}
                  companyId={companyId}
                />
              </div>
            ))}
          </div>
          <DialogFooter showCloseButton />
        </DialogContent>
      </Dialog>
    </div>
  )
}
