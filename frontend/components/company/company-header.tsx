"use client"

import { useTranslations } from "next-intl"
import type { ReactNode } from "react"

import { BackLink } from "@/components/back-link"
import { CompanyNav } from "@/components/company/company-nav"
import { LogoPicker } from "@/components/company/logo-picker"
import { VerifiedBadge } from "@/components/company/verified-badge"
import { VerifyCompany } from "@/components/company/verify-company"
import { EditableTitle } from "@/components/editable-title"
import { MAX_COMPANY_NAME_LENGTH } from "@/constants/limits"

export function CompanyHeader({
  companyId,
  name,
  logoUrl,
  verifiedDomain,
  websiteDomain,
  current,
  action,
}: {
  companyId: string
  name: string
  logoUrl: string | null
  // The verified domain (the badge), or the website still waiting for an admin's work email.
  verifiedDomain: string | null
  websiteDomain: string | null
  current: "interviews" | "templates" | "members" | "referrals"
  action?: ReactNode
}) {
  const t = useTranslations("company")

  return (
    <div className="space-y-4">
      <div className="relative flex min-h-14 items-center">
        <BackLink href="/company">{t("title")}</BackLink>
        {/* The logo candidates see; clicking it sets or changes it. */}
        <div className="me-4">
          <LogoPicker companyId={companyId} name={name} logoUrl={logoUrl} />
        </div>
        {/* Renamed in place, like a test's title; the name stays unique across prepza. Then the
            verified badge, or the way to verify. */}
        <div className="me-4 flex min-w-0 flex-1 items-center gap-3">
          <div className="min-w-0">
            <EditableTitle
              title={name}
              path={`/companies/companies/${companyId}/name`}
              maxLength={MAX_COMPANY_NAME_LENGTH}
            />
          </div>
          {verifiedDomain ? (
            <VerifiedBadge domain={verifiedDomain} className="size-7" />
          ) : (
            <VerifyCompany
              companyId={companyId}
              websiteDomain={websiteDomain}
            />
          )}
        </div>
        {action}
      </div>
      <CompanyNav companyId={companyId} current={current} />
    </div>
  )
}
