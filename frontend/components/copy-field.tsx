"use client"

import { CopyIcon } from "lucide-react"
import { useTranslations } from "next-intl"
import { toast } from "sonner"

import { InputAction } from "@/components/input-action"
import { useOrigin } from "@/lib/origin"

/** A link on this site (`path`), in a read-only field with a copy button. */
export function CopyField({ path }: { path: string }) {
  const common = useTranslations("common")
  const origin = useOrigin()
  const url = origin ? `${origin}${path}` : ""

  async function copy(event: React.FormEvent) {
    event.preventDefault()

    if (!url) {
      return
    }

    await navigator.clipboard.writeText(url)
    toast.success(common("linkCopied"))
  }

  return (
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
  )
}
