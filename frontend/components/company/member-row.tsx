"use client"

import { LinkIcon } from "lucide-react"
import { useTranslations } from "next-intl"
import { toast } from "sonner"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { useOrigin } from "@/lib/origin"
import type { CompanyMember } from "@/types/company"

export function MemberRow({ member }: { member: CompanyMember }) {
  const t = useTranslations("members")
  const common = useTranslations("common")
  const roles = useTranslations("roles")
  const origin = useOrigin()
  const url = origin && member.token ? `${origin}/join/${member.token}` : ""

  async function copy() {
    await navigator.clipboard.writeText(url)
    toast.success(common("linkCopied"))
  }

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
      {!member.joined && url && (
        <div className="flex items-center gap-2">
          <p className="min-w-0 flex-1 rounded-xl border px-2.5 py-2 font-mono text-xs break-all">
            {url}
          </p>
          <Button type="button" variant="outline" onClick={copy}>
            <LinkIcon />
            {t("copy")}
          </Button>
        </div>
      )}
    </div>
  )
}
