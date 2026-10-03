"use client"

import { useLocale, useTranslations } from "next-intl"

import { BuyButton } from "@/components/billing/buy-button"
import { CustomTopUp } from "@/components/billing/custom-top-up"
import { Badge } from "@/components/ui/badge"
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

/** The top-up button and its dialog of amounts, for the user's credits or `companyId`'s. */
export function TopUpDialog({
  catalog,
  title,
  companyId,
}: {
  catalog: Catalog
  // Whose credits: "Your credits" or the company's name.
  title: string
  companyId?: string
}) {
  const t = useTranslations("billing")
  const locale = useLocale()

  return (
    <Dialog>
      <DialogTrigger render={<Button className="h-10 px-5" />}>
        {t("topUp")}
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
                <p className="text-sm text-muted-foreground tabular-nums">
                  {t("credits", { count: product.credits })}
                </p>
                {product.bonus_credits > 0 && (
                  <Badge className="font-light">
                    {t("bonus", { count: product.bonus_credits })}
                  </Badge>
                )}
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
        <CustomTopUp catalog={catalog} companyId={companyId} />
        <DialogFooter showCloseButton />
      </DialogContent>
    </Dialog>
  )
}
