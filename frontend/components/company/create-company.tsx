"use client"

import { PlusIcon } from "lucide-react"
import { useRouter } from "next/navigation"
import { useTranslations } from "next-intl"
import { useState } from "react"
import { toast } from "sonner"

import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { apiErrorMessage, apiFetch } from "@/lib/api"
import type { Company } from "@/types/company"

export function CreateCompany() {
  const t = useTranslations("company")
  const common = useTranslations("common")
  const router = useRouter()
  const [open, setOpen] = useState(false)
  const [name, setName] = useState("")
  const [saving, setSaving] = useState(false)

  function handleOpen(next: boolean) {
    if (saving) {
      return
    }

    setOpen(next)

    if (!next) {
      setName("")
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
      toast.error(apiErrorMessage(error, t("createFailed")))
      setSaving(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={handleOpen}>
      <DialogTrigger
        render={
          <Button
            size="icon"
            className="size-14 rounded-full"
            aria-label={t("new")}
          />
        }
      >
        <PlusIcon className="size-6" />
      </DialogTrigger>
      <DialogContent showCloseButton={false} className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>{t("new")}</DialogTitle>
          <DialogDescription>{t("newText")}</DialogDescription>
        </DialogHeader>
        <form id="create-company-form" onSubmit={create}>
          <div className="rounded-lg border border-transparent transition-colors focus-within:border-ring">
            <Input
              required
              maxLength={200}
              placeholder={t("name")}
              aria-label={t("name")}
              value={name}
              onChange={(event) => setName(event.target.value)}
              className="h-16 border-0 px-6 text-lg focus-visible:ring-0 md:text-lg"
            />
          </div>
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
