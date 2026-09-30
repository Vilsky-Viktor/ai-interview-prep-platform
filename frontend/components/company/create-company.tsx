"use client"

import { PlusIcon } from "lucide-react"
import { useRouter } from "next/navigation"
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
import { apiFetch } from "@/lib/api"
import type { Company } from "@/types/company"

export function CreateCompany() {
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
    } catch {
      toast.error("Couldn't create the company. Please try again.")
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
            aria-label="New company"
          />
        }
      >
        <PlusIcon className="size-6" />
      </DialogTrigger>
      <DialogContent showCloseButton={false} className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>New company</DialogTitle>
          <DialogDescription>
            Create a company to generate interviews and invite candidates.
          </DialogDescription>
        </DialogHeader>
        <form id="create-company-form" onSubmit={create}>
          <div className="rounded-lg border border-transparent transition-colors focus-within:border-ring">
            <Input
              required
              maxLength={200}
              placeholder="Company name"
              aria-label="Company name"
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
            Cancel
          </DialogClose>
          <Button
            type="submit"
            form="create-company-form"
            className="h-10 px-5 text-base"
            disabled={saving || !name.trim()}
          >
            Create
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
