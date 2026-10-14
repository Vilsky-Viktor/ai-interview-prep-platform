"use client"

import { useTranslations } from "next-intl"

import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip"

/** A balance's number, which says "Current balance" on hover, and `note` under it (that it runs
 * low). */
export function BalanceTooltip({
  className,
  note,
  children,
}: {
  className?: string
  note?: string
  children: React.ReactNode
}) {
  const t = useTranslations("billing")

  return (
    <Tooltip>
      <TooltipTrigger render={<span className={className} />}>
        {children}
      </TooltipTrigger>
      <TooltipContent>
        <p>{t("currentBalance")}</p>
        {note && <p>{note}</p>}
      </TooltipContent>
    </Tooltip>
  )
}
