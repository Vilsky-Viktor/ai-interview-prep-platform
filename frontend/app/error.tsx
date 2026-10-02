"use client"

import * as Sentry from "@sentry/nextjs"
import Link from "next/link"
import { useEffect } from "react"

import { Button } from "@/components/ui/button"

export default function ErrorPage({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    Sentry.captureException(error)
  }, [error])

  return (
    <main className="mx-auto flex min-h-[calc(100svh-3.5rem)] w-full max-w-5xl flex-col items-center justify-center px-6 py-12">
      <div className="w-full space-y-8 text-center">
        <div className="space-y-4">
          <h1 className="font-heading text-4xl font-medium tracking-tight text-balance sm:text-5xl">
            Something went wrong
          </h1>
          <p className="text-base text-muted-foreground">
            Please try again. If it keeps happening, come back later.
          </p>
        </div>
        <div className="flex justify-center gap-3">
          <Button className="h-12 px-6 text-base" onClick={reset}>
            Try again
          </Button>
          <Button
            variant="outline"
            className="h-12 px-6 text-base"
            render={<Link href="/" />}
            nativeButton={false}
          >
            Home
          </Button>
        </div>
      </div>
    </main>
  )
}
