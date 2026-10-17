"use client"

import { CheckIcon, CopyIcon } from "lucide-react"
import { useTranslations } from "next-intl"

import { DropdownMenuItem } from "@/components/ui/dropdown-menu"
import { useCopyId } from "@/hooks/use-copy-id"

/** "copy id" in a menu: a small outline pill under the account's email, as wide as the menu, a
 * real menu item (the arrow keys reach it) that keeps the menu open while its check mark shows. */
export function CopyIdItem({ id }: { id: string }) {
  const common = useTranslations("common")
  const { copied, copy } = useCopyId(id)

  return (
    <DropdownMenuItem
      closeOnClick={false}
      onClick={copy}
      aria-label={common(copied ? "idCopied" : "copyId")}
      data-testid="copy-id"
      data-copied={copied}
      className="mb-2 h-7 justify-center gap-1 rounded-full border px-3 text-xs lowercase [&_svg:not([class*='size-'])]:size-3.5"
    >
      {common("copyId")}
      {copied ? (
        <CheckIcon aria-hidden className="text-primary" />
      ) : (
        <CopyIcon aria-hidden />
      )}
    </DropdownMenuItem>
  )
}
