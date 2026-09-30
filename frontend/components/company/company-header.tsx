import type { ReactNode } from "react"

import { BackLink } from "@/components/back-link"
import { CompanyNav } from "@/components/company/company-nav"

export function CompanyHeader({
  companyId,
  name,
  current,
  action,
}: {
  companyId: string
  name: string
  current: "interviews" | "members"
  action?: ReactNode
}) {
  return (
    <div className="space-y-4">
      <div className="relative flex min-h-14 items-center">
        <BackLink href="/company">Companies</BackLink>
        <h1 className="min-w-0 flex-1 font-heading text-3xl font-medium tracking-tight">
          {name}
        </h1>
        {action}
      </div>
      <CompanyNav companyId={companyId} current={current} />
    </div>
  )
}
