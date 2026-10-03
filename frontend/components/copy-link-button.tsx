"use client"

import { LinkIcon } from "lucide-react"
import { useTranslations } from "next-intl"
import { toast } from "sonner"

import { Button } from "@/components/ui/button"

export function CopyLinkButton() {
  const t = useTranslations("common")

  async function copy() {
    await navigator.clipboard.writeText(location.href)
    toast.success(t("linkCopied"))
  }

  return (
    <Button variant="outline" onClick={copy}>
      <LinkIcon />
      {t("copyLink")}
    </Button>
  )
}
