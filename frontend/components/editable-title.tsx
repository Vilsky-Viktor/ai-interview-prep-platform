"use client"

import { useRouter } from "next/navigation"
import { useTranslations } from "next-intl"
import { useEffect, useRef, useState } from "react"
import { toast } from "sonner"

import { MAX_TITLE_LENGTH } from "@/constants/limits"
import { ApiError, apiErrorMessage, apiFetch } from "@/lib/api"

const titleClass =
  "font-heading text-3xl font-medium tracking-tight text-balance normal-case"

/** A page's title, edited in place: `path` takes {"title"}. `maxLength` defaults to a test's
 * title limit (a company's name is shorter). Not `editable` (a viewer), it's a plain title. */
export function EditableTitle({
  title,
  path,
  maxLength = MAX_TITLE_LENGTH,
  editable = true,
}: {
  title: string
  path: string
  maxLength?: number
  editable?: boolean
}) {
  const t = useTranslations("common")
  const router = useRouter()
  const inputRef = useRef<HTMLInputElement>(null)
  const skipSave = useRef(false)
  const savingRef = useRef(false)
  const [editing, setEditing] = useState(false)
  const [value, setValue] = useState(title)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    if (!editing) {
      return
    }

    const input = inputRef.current

    if (!input) {
      return
    }

    const end = input.value.length

    input.focus()
    input.setSelectionRange(end, end)
  }, [editing])

  async function save() {
    const next = value.trim()

    if (savingRef.current) {
      return
    }

    if (!next || next === title) {
      setValue(title)
      setEditing(false)

      return
    }

    savingRef.current = true
    setSaving(true)

    try {
      await apiFetch(path, {
        method: "PATCH",
        body: JSON.stringify({ title: next }),
      })
      setEditing(false)
      router.refresh()
    } catch (error) {
      // Says why, e.g. when another company already has the name.
      const refused = error instanceof ApiError && error.status === 409
      toast.error(
        refused ? error.message : apiErrorMessage(error, t("titleFailed"))
      )
    } finally {
      savingRef.current = false
      setSaving(false)
    }
  }

  function cancel() {
    skipSave.current = true
    setValue(title)
    setEditing(false)
  }

  if (!editable) {
    return <h1 className={titleClass}>{title}</h1>
  }

  if (!editing) {
    return (
      <h1 className={titleClass}>
        <button
          type="button"
          className="inline cursor-text text-start normal-case"
          onClick={() => {
            setValue(title)
            setEditing(true)
          }}
        >
          {title}
        </button>
      </h1>
    )
  }

  return (
    <input
      ref={inputRef}
      maxLength={maxLength}
      aria-label={t("title")}
      disabled={saving}
      value={value}
      className={`${titleClass} w-full min-w-0 rounded-full border border-ring bg-transparent px-4 py-1 outline-none`}
      onChange={(event) => setValue(event.target.value)}
      onBlur={() => {
        if (skipSave.current) {
          skipSave.current = false

          return
        }

        void save()
      }}
      onKeyDown={(event) => {
        if (event.key === "Enter") {
          event.preventDefault()
          event.currentTarget.blur()
        }

        if (event.key === "Escape") {
          event.preventDefault()
          cancel()
        }
      }}
    />
  )
}
