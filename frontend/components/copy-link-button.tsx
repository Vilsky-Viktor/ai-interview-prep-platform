"use client"

import { LinkIcon } from "lucide-react"
import { toast } from "sonner"

import { Button } from "@/components/ui/button"

export function CopyLinkButton() {
  async function copy() {
    await navigator.clipboard.writeText(location.href)
    toast.success("Link copied")
  }

  return (
    <Button variant="outline" onClick={copy}>
      <LinkIcon />
      Copy link
    </Button>
  )
}
