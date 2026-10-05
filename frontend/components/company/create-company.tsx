"use client"

import { cn } from "cn"
import { useRouter } from "next/navigation"
import { useTranslations } from "next-intl"
import { useState } from "react"
import { toast } from "sonner"

import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { MAX_COMPANY_NAME_LENGTH } from "@/constants/limits"
import { ApiError, apiErrorMessage, apiFetch } from "@/lib/api"
import type { Company } from "@/types/company"

export function CreateCompany() {
  const t = useTranslations("company")
  const common = useTranslations("common")
  const router = useRouter()
  const [open, setOpen] = useState(false)
  const [name, setName] = useState("")
  const [saving, setSaving] = useState(false)
  // The server's reason the name can't be used (it's taken), shown under the field.
  const [nameError, setNameError] = useState<string | null>(null)

  function handleOpen(next: boolean) {
    if (saving) {
      return
    }

    setOpen(next)

    if (!next) {
      setName("")
      setNameError(null)
    }
  }

  async function create(event: React.FormEvent) {
    event.preventDefault()

    if (!name.trim() || saving) {
      return
    }

    setSaving(true)

    try {
      const company = await apiFetch<Company>("/companies/companies", {
        method: "POST",
        body: JSON.stringify({ name: name.trim() }),
      })
      router.replace(`/company/${company.id}/interviews`)
    } catch (error) {
      if (error instanceof ApiError && error.status === 409) {
        setNameError(error.message)
      } else {
        toast.error(apiErrorMessage(error, t("createFailed")))
      }

      setSaving(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={handleOpen}>
      <DialogTrigger render={<Button className="h-12 px-6 text-base" />}>
        {t("new")}
      </DialogTrigger>
      <DialogContent showCloseButton={false} className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>{t("new")}</DialogTitle>
        </DialogHeader>
        <form id="create-company-form" onSubmit={create}>
          <div
            className={cn(
              "rounded-full border border-transparent transition-colors focus-within:border-ring",
              nameError && "border-destructive focus-within:border-destructive"
            )}
          >
            <Input
              required
              maxLength={MAX_COMPANY_NAME_LENGTH}
              placeholder={t("name")}
              aria-label={t("name")}
              value={name}
              onChange={(event) => {
                setName(event.target.value)
                setNameError(null)
              }}
              aria-invalid={nameError !== null}
              aria-describedby={nameError ? "company-name-error" : undefined}
              className="h-16 border-0 px-6 text-lg focus-visible:ring-0 md:text-lg"
            />
          </div>
          {nameError && (
            <p
              id="company-name-error"
              role="alert"
              className="px-6 pt-2 text-sm text-destructive"
            >
              {nameError}
            </p>
          )}
        </form>
        <DialogFooter>
          <DialogClose
            render={
              <Button
                variant="outline"
                className="h-10 px-5 text-base"
                disabled={saving}
              />
            }
          >
            {common("cancel")}
          </DialogClose>
          <Button
            type="submit"
            form="create-company-form"
            className="h-10 px-5 text-base"
            disabled={saving || !name.trim()}
          >
            {t("create")}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
