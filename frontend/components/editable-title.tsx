"use client"

import { useRouter } from "next/navigation"
import { useEffect, useRef, useState } from "react"
import { toast } from "sonner"

import { apiFetch } from "@/lib/api"

const titleClass =
  "font-heading text-3xl font-medium tracking-tight text-balance"

export function EditableTitle({ title, path }: { title: string; path: string }) {
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
    } catch {
      toast.error("Couldn't save the title.")
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

  if (!editing) {
    return (
      <h1 className={titleClass}>
        <button
          type="button"
          className="cursor-text text-left"
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
      maxLength={200}
      aria-label="Title"
      disabled={saving}
      value={value}
      className={`${titleClass} w-full min-w-0 rounded-lg border border-ring bg-transparent px-3 py-1 outline-none`}
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
