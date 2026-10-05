"use client"

import { Button } from "@/components/ui/button"

/** Back up to the job description box at the top of the home page, ready to type. */
export function StartButton({ label }: { label: string }) {
  function start() {
    window.scrollTo({ top: 0, behavior: "smooth" })
    document.querySelector("textarea")?.focus({ preventScroll: true })
  }

  return (
    <Button className="h-12 px-8 text-base" onClick={start}>
      {label}
    </Button>
  )
}
