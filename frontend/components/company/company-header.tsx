"use client"

import { useTranslations } from "next-intl"
import type { ReactNode } from "react"

import { BackLink } from "@/components/back-link"
import { CompanyNav } from "@/components/company/company-nav"
import { LogoPicker } from "@/components/company/logo-picker"
import { PendingBadge } from "@/components/company/pending-badge"
import { VerifiedBadge } from "@/components/company/verified-badge"
import { VerifyCompany } from "@/components/company/verify-company"
import { EditableTitle } from "@/components/editable-title"
import { MAX_COMPANY_NAME_LENGTH } from "@/constants/limits"
import type { VerificationStatus } from "@/types/company"

export function CompanyHeader({
  companyId,
  name,
  logoUrl,
  verifiedDomain,
  websiteDomain,
  verificationStatus,
  declineReason,
  current,
  action,
  canEdit,
}: {
  companyId: string
  name: string
  logoUrl: string | null
  // The verified domain (the badge); else the website, where its verification stands and why a
  // superadmin declined it.
  verifiedDomain: string | null
  websiteDomain: string | null
  verificationStatus: VerificationStatus
  declineReason: string | null
  current: "interviews" | "templates" | "members" | "integrations" | "referrals"
  action?: ReactNode
  // Owners and admins change the logo, name and website; viewers only see them.
  canEdit: boolean
}) {
  const t = useTranslations("company")
  const verify = useTranslations("verify")
  // A rename sends a verified, pending or declined company for review again.
  const reviewed = ["approved", "pending", "declined"].includes(
    verificationStatus ?? ""
  )

  return (
    <div className="space-y-4">
      <div className="relative flex min-h-14 items-center">
        <BackLink href="/companies">{t("title")}</BackLink>
        {/* The logo candidates see; clicking it sets or changes it. */}
        <div className="me-4">
          <LogoPicker
            companyId={companyId}
            name={name}
            logoUrl={logoUrl}
            editable={canEdit}
          />
        </div>
        {/* Renamed in place, like a test's title; the name stays unique across prepza. Then the
            verified badge, the pending one while a superadmin reviews it, or the way to verify. */}
        <div className="me-4 flex min-w-0 flex-1 items-center gap-3">
          <div className="min-w-0">
            <EditableTitle
              title={name}
              path={`/companies/companies/${companyId}/name`}
              maxLength={MAX_COMPANY_NAME_LENGTH}
              editable={canEdit}
              hint={reviewed ? verify("renameHint") : undefined}
            />
          </div>
          {verifiedDomain ? (
            <VerifiedBadge domain={verifiedDomain} className="size-7" />
          ) : canEdit ? (
            <VerifyCompany
              companyId={companyId}
              websiteDomain={websiteDomain}
              status={verificationStatus}
              declineReason={declineReason}
            />
          ) : (
            verificationStatus === "pending" && (
              <PendingBadge className="size-7" />
            )
          )}
        </div>
        {action}
      </div>
      <CompanyNav companyId={companyId} current={current} />
    </div>
  )
}
