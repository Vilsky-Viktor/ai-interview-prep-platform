"use client"

import { cn } from "cn"
import Link from "next/link"
import { useFormatter, useLocale, useTranslations } from "next-intl"

import { InvoiceLink } from "@/components/billing/invoice-link"
import { formatDate, formatPrice } from "@/lib/format"
import type { CreditHistoryEntry } from "@/types/company"

/** One movement of a company's credits: what it was, when, and the credits it moved; a top-up
 * with what was paid and its invoice, a candidate's charge with the candidate and their test. */
export function HistoryRow({
  companyId,
  entry,
}: {
  companyId: string
  entry: CreditHistoryEntry
}) {
  const t = useTranslations("companyBilling")
  const format = useFormatter()
  const locale = useLocale()
  const candidate = entry.candidate

  const content = (
    // On phones the amount goes under the rest, everything centered.
    <span className="flex items-center justify-between gap-4 p-6 max-sm:flex-col max-sm:text-center">
      <span className="min-w-0 space-y-1">
        {/* A candidate's charge leads with the candidate, like the candidate lists. */}
        <span className="block text-lg font-medium break-all normal-case">
          {candidate
            ? (candidate.name ?? candidate.email)
            : t(`reasons.${entry.reason}`)}
        </span>
        {candidate && (
          <span className="block text-sm break-all text-muted-foreground normal-case">
            {[candidate.name && candidate.email, candidate.interview_title]
              .filter(Boolean)
              .join(" · ")}
          </span>
        )}
        {entry.candidate_deleted && (
          <span className="block text-sm text-muted-foreground">
            {t("deletedCandidate")}
          </span>
        )}
        <span className="flex flex-wrap items-center gap-x-4 gap-y-1 text-sm text-muted-foreground max-sm:justify-center">
          <time dateTime={entry.created_at} suppressHydrationWarning>
            {formatDate(entry.created_at, locale)}
          </time>
          {entry.total != null && entry.currency && (
            <span className="tabular-nums">
              {formatPrice(Number(entry.total), entry.currency, locale)}
            </span>
          )}
          {entry.automatic && <span>{t("automatic")}</span>}
          {entry.invoice_id && (
            <InvoiceLink
              companyId={companyId}
              transactionId={entry.invoice_id}
            />
          )}
        </span>
      </span>
      <span
        className={cn(
          "shrink-0 font-heading text-2xl font-medium tabular-nums",
          entry.amount > 0 && "text-primary"
        )}
      >
        {format.number(entry.amount, { signDisplay: "exceptZero" })}
      </span>
    </span>
  )

  // A candidate's charge opens the candidate.
  return candidate ? (
    <Link
      href={`/companies/${companyId}/interviews/${candidate.interview_id}/candidates/${candidate.invite_id}`}
      className="block transition-colors hover:bg-muted/50 active:bg-muted/50"
    >
      {content}
    </Link>
  ) : (
    content
  )
}
