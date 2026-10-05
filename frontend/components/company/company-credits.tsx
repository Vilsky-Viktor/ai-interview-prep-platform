"use client"

import { cn } from "cn"
import { useLocale, useTranslations } from "next-intl"

import { RefreshOnFocus } from "@/components/billing/refresh-on-focus"
import { TopUpDialog } from "@/components/billing/top-up-dialog"
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip"
import { useCountUp } from "@/hooks/use-count-up"
import type { Catalog } from "@/types/billing"

/** The company's credits for candidates, with a top-up next to them, in the page header. */
export function CompanyCredits({
  companyId,
  companyName,
  credits,
  low,
  catalog,
}: {
  companyId: string
  companyName: string
  credits: number
  low: boolean
  catalog: Catalog
}) {
  const t = useTranslations("company")
  const locale = useLocale()
  // A top-up arriving counts up, as in the header.
  const { shown, rising } = useCountUp(credits)

  // A small card in the page header: the balance (amber when it runs low); it opens the top-up.
  return (
    <>
      <TopUpDialog
        catalog={catalog}
        title={companyName}
        companyId={companyId}
        card={
          <span className="text-base text-muted-foreground">
            <Tooltip disabled={!low}>
              <TooltipTrigger
                render={
                  <span
                    className={cn(
                      "font-medium text-foreground tabular-nums transition-colors duration-500",
                      rising && "text-primary",
                      low && "text-amber-600 dark:text-amber-400"
                    )}
                  />
                }
              >
                {shown.toLocaleString(locale)}
              </TooltipTrigger>
              <TooltipContent>{t("creditsLow")}</TooltipContent>
            </Tooltip>{" "}
            {t("creditsLeft", { count: credits })}
          </span>
        }
      />
      <RefreshOnFocus />
    </>
  )
}
