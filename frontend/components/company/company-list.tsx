"use client"

import { MessagesSquareIcon, UserRoundIcon } from "lucide-react"
import Link from "next/link"
import { useTranslations } from "next-intl"

import { RemoveCompany } from "@/components/company/remove-company"
import { Badge } from "@/components/ui/badge"
import { VirtualList } from "@/components/virtual-list"
import { usePagedList } from "@/hooks/use-paged-list"
import type { Company } from "@/types/company"

const PATH = "/companies/companies"

/** The companies the user belongs to, a page at a time; `initial` is the server's first page. */
export function CompanyList({ initial }: { initial: Company[] }) {
  const t = useTranslations("company")
  const roles = useTranslations("roles")
  const { items, loadMore } = usePagedList(PATH, initial)

  if (items.length === 0) {
    return (
      <p className="rounded-2xl border p-6 text-muted-foreground">
        {t("empty")}
      </p>
    )
  }

  return (
    <VirtualList
      items={items}
      getKey={(company) => company.id}
      estimateSize={81}
      onEndReached={loadMore}
      className="divide-y rounded-2xl border"
      renderItem={(company) => (
        // One hover surface: the link stretches over the whole row, Remove sits on top of it.
        <div className="relative flex items-center gap-2 p-6 pe-3 transition-colors hover:bg-muted/50">
          <Link
            href={`/company/${company.id}/interviews`}
            className="flex min-w-0 flex-1 items-center justify-between gap-4 after:absolute after:inset-0"
          >
            <span className="flex min-w-0 items-center gap-2">
              <span className="text-xl font-medium">{company.name}</span>
              {company.role === "owner" && (
                <span
                  role="img"
                  aria-label={t("owner")}
                  className="text-muted-foreground"
                >
                  <UserRoundIcon className="size-5" />
                </span>
              )}
            </span>
            <span className="flex shrink-0 items-center gap-4">
              <span
                className="flex items-center gap-1.5 text-sm text-muted-foreground tabular-nums"
                aria-label={t("interviewCount", {
                  count: company.interview_count,
                })}
              >
                <MessagesSquareIcon aria-hidden className="size-5" />
                {company.interview_count}
              </span>
              {company.role !== "owner" && (
                <Badge
                  variant="secondary"
                  className="h-7 px-3 text-sm font-light"
                >
                  {roles(company.role)}
                </Badge>
              )}
            </span>
          </Link>
          {company.role === "owner" && (
            <div className="relative z-10 shrink-0">
              <RemoveCompany companyId={company.id} name={company.name} />
            </div>
          )}
        </div>
      )}
    />
  )
}
