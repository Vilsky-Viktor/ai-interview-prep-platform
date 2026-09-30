"use client"

import type { ReactNode } from "react"
import { ArrowLeftIcon } from "lucide-react"
import Link from "next/link"

import { Button } from "@/components/ui/button"

export function BackLink({
  href,
  children,
}: {
  href: string
  children: ReactNode
}) {
  const label = typeof children === "string" ? children : "Back"

  return (
    <Button
      variant="ghost"
      size="icon-lg"
      aria-label={label}
      // Beside the title only when the page margin fits it; above the title otherwise.
      className="mb-2 -ml-3 size-11 rounded-xl text-muted-foreground xl:absolute xl:top-1/2 xl:right-[calc(100%+0.25rem)] xl:mb-0 xl:ml-0 xl:size-14 xl:-translate-y-1/2"
      render={<Link href={href} />}
      nativeButton={false}
    >
      <ArrowLeftIcon className="size-6 xl:size-8" />
    </Button>
  )
}
