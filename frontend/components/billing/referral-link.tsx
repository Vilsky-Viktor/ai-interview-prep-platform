"use client"

import { CopyIcon } from "lucide-react"
import { useTranslations } from "next-intl"
import { toast } from "sonner"

import { InputAction } from "@/components/input-action"
import { useOrigin } from "@/lib/origin"
import type { Referral } from "@/types/billing"

/** A referral link to copy, opening `path` (home for learners, the hiring page for companies),
 * and how many times it has paid off. */
export function ReferralLink({
  referral,
  path,
}: {
  referral: Referral
  path: string
}) {
  const t = useTranslations("referral")
  const common = useTranslations("common")
  const origin = useOrigin()
  const url = origin ? `${origin}${path}?ref=${referral.code}` : ""

  async function copy(event: React.FormEvent) {
    event.preventDefault()

    if (!url) {
      return
    }

    await navigator.clipboard.writeText(url)
    toast.success(common("linkCopied"))
  }

  return (
    <div className="space-y-6">
      <form onSubmit={copy} className="flex">
        <InputAction
          readOnly
          value={url}
          aria-label={common("copyLink")}
          action={common("copyLink")}
          disabled={!url}
          icon={<CopyIcon className="size-5" />}
          onFocus={(event) => event.target.select()}
        />
      </form>
      <p className="text-center text-sm text-muted-foreground">
        {t("rewarded", { count: referral.rewarded })}
      </p>
    </div>
  )
}
