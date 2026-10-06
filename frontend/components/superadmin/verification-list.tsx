"use client"

import { useRouter } from "next/navigation"
import { useLocale, useTranslations } from "next-intl"

import { DeclineVerification } from "@/components/superadmin/decline-verification"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { VirtualList } from "@/components/virtual-list"
import { usePagedList } from "@/hooks/use-paged-list"
import { apiFetch } from "@/lib/api"
import { decisionFailed } from "@/lib/verification"
import { formatDate } from "@/lib/format"
import type { VerificationRequest } from "@/types/superadmin"

function rowKey(row: VerificationRequest) {
  return row.company_id
}

/** Companies sent for review, a page at a time in the API's order (pending first, then those
 * decided): the name and website to check, the work email that proved the domain, and when.
 * A pending one is approved or declined here; one that changed meanwhile reloads instead. */
export function VerificationList({
  path,
  initial,
}: {
  path: string
  initial: VerificationRequest[]
}) {
  const t = useTranslations("superadmin")
  const locale = useLocale()
  const router = useRouter()
  const { items, loadMore } = usePagedList<VerificationRequest>(
    path,
    rowKey,
    initial
  )

  async function approve(row: VerificationRequest) {
    try {
      // The name and domain shown here: a request changed since isn't approved.
      await apiFetch(
        `/companies/superadmin/verifications/${row.company_id}/approve`,
        {
          method: "POST",
          body: JSON.stringify({ name: row.name, domain: row.domain }),
        }
      )
      router.refresh()
    } catch (error) {
      decisionFailed(
        error,
        { changed: t("requestChanged"), failed: t("actionFailed") },
        router.refresh
      )
    }
  }

  if (items.length === 0) {
    return (
      <p className="py-10 text-center text-muted-foreground">
        {t("noVerifications")}
      </p>
    )
  }

  return (
    <VirtualList
      items={items}
      getKey={rowKey}
      estimateSize={120}
      onEndReached={loadMore}
      className="divide-y rounded-2xl border"
      renderItem={(row) => {
        const date =
          row.status === "pending" ? row.submitted_at : row.decided_at

        return (
          <div className="flex items-center gap-6 p-6">
            <div className="min-w-0 flex-1 space-y-1">
              <p className="text-lg font-medium">{row.name}</p>
              <p className="text-sm break-words text-muted-foreground">
                <a
                  href={`https://${row.domain}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="underline underline-offset-4 hover:text-foreground"
                >
                  {row.domain}
                </a>
                {row.email && ` · ${row.email}`}
                {date && (
                  <>
                    {" · "}
                    <time dateTime={date} suppressHydrationWarning>
                      {formatDate(date, locale)}
                    </time>
                  </>
                )}
              </p>
              {row.decline_reason && (
                <p className="text-sm text-muted-foreground">
                  {t("declinedBecause", { reason: row.decline_reason })}
                </p>
              )}
            </div>
            <div className="flex shrink-0 flex-col items-end gap-2">
              <Badge variant="outline" className="h-7 px-3 text-sm font-light">
                {t(`verificationStatus.${row.status}`)}
              </Badge>
              {row.status === "pending" && (
                <span className="flex gap-2 pt-1">
                  <DeclineVerification
                    companyId={row.company_id}
                    name={row.name}
                  />
                  <Button
                    variant="outline"
                    size="sm"
                    className="h-8 px-3 text-sm"
                    onClick={() => approve(row)}
                  >
                    {t("approve")}
                  </Button>
                </span>
              )}
            </div>
          </div>
        )
      }}
    />
  )
}
