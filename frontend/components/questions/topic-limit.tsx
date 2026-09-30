"use client"

import { useRouter } from "next/navigation"
import { useState } from "react"
import { toast } from "sonner"

import { Input } from "@/components/ui/input"
import { apiErrorMessage, apiFetch } from "@/lib/api"

export function TopicLimit({
  path,
  count,
  limit,
}: {
  path: string
  count: number
  limit: number | null
}) {
  const router = useRouter()
  const saved = String(limit ?? count)
  const [value, setValue] = useState(saved)
  const [saving, setSaving] = useState(false)

  async function save() {
    const number = Number(value.trim())

    if (value.trim() === saved) {
      return
    }

    if (!Number.isInteger(number) || number < 1 || number > count) {
      toast.error(`Enter a number from 1 to ${count}.`)
      setValue(saved)

      return
    }

    const next = number === count ? null : number

    setSaving(true)

    try {
      await apiFetch(path, {
        method: "PUT",
        body: JSON.stringify({ limit: next }),
      })
      router.refresh()
    } catch (error) {
      setValue(saved)
      toast.error(apiErrorMessage(error, "Couldn't save the limit."))
    } finally {
      setSaving(false)
    }
  }

  return (
    <Input
      type="number"
      inputMode="numeric"
      min={1}
      max={count}
      value={value}
      disabled={saving}
      aria-label="Question limit"
      className="h-9 w-14 border-0 bg-muted px-1 text-center text-lg text-foreground tabular-nums md:text-lg dark:bg-muted [appearance:textfield] [&::-webkit-inner-spin-button]:appearance-none [&::-webkit-outer-spin-button]:appearance-none"
      onChange={(event) => setValue(event.target.value)}
      onBlur={save}
      onKeyDown={(event) => {
        if (event.key === "Enter") {
          event.currentTarget.blur()
        }
      }}
    />
  )
}
