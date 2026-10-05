"use client"

import { ImageUpIcon, Trash2Icon } from "lucide-react"
import { useRouter } from "next/navigation"
import { useTranslations } from "next-intl"
import { useRef, useState } from "react"
import { toast } from "sonner"

import { CompanyLogo } from "@/components/company/company-logo"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip"
import { ApiError, apiFetch } from "@/lib/api"
import { fileBase64 } from "@/lib/files"

const SPOT =
  "flex size-12 shrink-0 cursor-pointer items-center justify-center overflow-hidden rounded-xl bg-muted transition-colors hover:bg-muted/70 disabled:cursor-default"

/** The company's logo beside its name: without one, its first letter, and a click picks an
 * image; with one, a click offers to change or remove it. */
export function LogoPicker({
  companyId,
  name,
  logoUrl,
}: {
  companyId: string
  name: string
  logoUrl: string | null
}) {
  const t = useTranslations("company")
  const router = useRouter()
  const fileInput = useRef<HTMLInputElement>(null)
  const [saving, setSaving] = useState(false)
  const path = `/companies/companies/${companyId}/logo`

  async function save(request: () => Promise<unknown>) {
    setSaving(true)

    try {
      await request()
      router.refresh()
    } catch (error) {
      // A file that isn't a PNG, JPEG or WebP up to 500 KB: the API says so.
      const invalid = error instanceof ApiError && error.status < 500
      toast.error(invalid ? error.message : t("logoFailed"))
    } finally {
      setSaving(false)
    }
  }

  function upload(file: File | undefined) {
    if (file) {
      save(async () =>
        apiFetch(path, {
          method: "PUT",
          body: JSON.stringify({ image: await fileBase64(file) }),
        })
      )
    }
  }

  const picker = (
    <input
      ref={fileInput}
      type="file"
      accept="image/png,image/jpeg,image/webp"
      className="hidden"
      onChange={(event) => {
        upload(event.target.files?.[0])
        event.target.value = ""
      }}
    />
  )

  if (!logoUrl) {
    return (
      <>
        <Tooltip>
          <TooltipTrigger
            render={
              <button
                type="button"
                className={SPOT}
                disabled={saving}
                aria-label={t("uploadLogo")}
                onClick={() => fileInput.current?.click()}
              />
            }
          >
            <span className="font-heading text-2xl font-medium text-muted-foreground uppercase">
              {name.slice(0, 1)}
            </span>
          </TooltipTrigger>
          <TooltipContent>{t("uploadLogo")}</TooltipContent>
        </Tooltip>
        {picker}
      </>
    )
  }

  return (
    <>
      <DropdownMenu>
        <DropdownMenuTrigger
          render={
            <button
              type="button"
              className={SPOT}
              disabled={saving}
              aria-label={t("logo")}
            />
          }
        >
          <CompanyLogo
            url={logoUrl}
            name={name}
            className="size-full object-contain"
          />
        </DropdownMenuTrigger>
        <DropdownMenuContent align="start" className="w-48 p-2">
          <DropdownMenuItem
            className="px-3 py-2"
            onClick={() => fileInput.current?.click()}
          >
            <ImageUpIcon />
            {t("changeLogo")}
          </DropdownMenuItem>
          <DropdownMenuItem
            className="px-3 py-2"
            onClick={() => save(() => apiFetch(path, { method: "DELETE" }))}
          >
            <Trash2Icon />
            {t("removeLogo")}
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
      {picker}
    </>
  )
}
