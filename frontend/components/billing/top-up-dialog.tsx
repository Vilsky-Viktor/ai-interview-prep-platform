"use client"

import { useLocale, useTranslations } from "next-intl"
import type { ReactNode } from "react"

import { BuyButton } from "@/components/billing/buy-button"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { formatPrice } from "@/lib/format"
import type { Catalog } from "@/types/billing"

/** The top-up button and its dialog of amounts, for `companyId`'s credits. */
export function TopUpDialog({
  catalog,
  title,
  companyId,
  card,
}: {
  catalog: Catalog
  // Whose credits: "Your credits" or the company's name.
  title: string
  companyId: string
  // Opens from this card (a balance in a page header) instead of a button.
  card?: ReactNode
}) {
  const t = useTranslations("billing")
  const locale = useLocale()

  return (
    <Dialog>
      <DialogTrigger
        render={
          card ? (
            <button
              type="button"
              className="cursor-pointer rounded-xl border px-4 py-2 text-end whitespace-nowrap transition-colors hover:bg-muted max-sm:text-center"
            />
          ) : (
            <Button className="h-10 px-5" />
          )
        }
      >
        {card ?? t("topUp")}
      </DialogTrigger>
      <DialogContent showCloseButton={false} className="sm:max-w-2xl">
        <DialogHeader>
          <DialogTitle>{t("topUpTitle", { name: title })}</DialogTitle>
          <DialogDescription className="text-base">
            {t("topUpNote")}
          </DialogDescription>
        </DialogHeader>
        <div className="grid gap-3 sm:grid-cols-2">
          {catalog.products.map((product) => (
            <div
              key={product.key}
              className="flex items-center justify-between gap-4 rounded-2xl border p-5 transition-colors hover:border-ring"
            >
              <div className="min-w-0 space-y-1">
                <p className="font-heading text-2xl font-medium tabular-nums">
                  {formatPrice(product.price_cents, catalog.currency, locale)}
                </p>
                <p className="text-base tabular-nums">
                  {t("candidates", { count: product.candidates })}
                </p>
                <p className="text-sm text-muted-foreground tabular-nums">
                  {t("each", {
                    price: formatPrice(
                      product.candidate_cents,
                      catalog.currency,
                      locale
                    ),
                  })}
                </p>
              </div>
              <BuyButton
                catalog={catalog}
                priceId={product.price_id}
                companyId={companyId}
                className="h-10 px-5"
              />
            </div>
          ))}
        </div>
        <DialogFooter showCloseButton />
      </DialogContent>
    </Dialog>
  )
}
