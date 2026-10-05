"use client"

import { useTranslations } from "next-intl"

import { CopyField } from "@/components/copy-field"
import { Badge } from "@/components/ui/badge"
import type { CompanyMember } from "@/types/company"

export function MemberRow({ member }: { member: CompanyMember }) {
  const t = useTranslations("members")
  const roles = useTranslations("roles")

  return (
    <div className="space-y-3 p-6">
      <div className="flex items-center justify-between gap-4">
        <span>
          <span className="block text-lg font-medium">{member.email}</span>
          <span className="text-sm text-muted-foreground">
            {member.joined ? t("joined") : t("invited")}
          </span>
        </span>
        <Badge variant="secondary" className="h-7 px-3 text-sm font-light">
          {roles(member.role)}
        </Badge>
      </div>
      {/* The join link in the site's copy field, like the test's shareable link. */}
      {!member.joined && member.token && (
        <CopyField path={`/join/${member.token}`} />
      )}
    </div>
  )
}
