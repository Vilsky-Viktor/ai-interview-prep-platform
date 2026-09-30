import Link from "next/link"

import { Button } from "@/components/ui/button"

export default function NotFound() {
  return (
    <main className="mx-auto flex min-h-[calc(100svh-3.5rem)] w-full max-w-5xl flex-col items-center justify-center px-6 py-12">
      <div className="w-full space-y-8 text-center">
        <div className="space-y-4">
          <h1 className="font-heading text-4xl font-medium tracking-tight text-balance sm:text-5xl">
            Page not found
          </h1>
          <p className="text-base text-muted-foreground">
            That page doesn&apos;t exist or was removed.
          </p>
        </div>
        <Button
          className="h-12 px-6 text-base"
          render={<Link href="/" />}
          nativeButton={false}
        >
          Home
        </Button>
      </div>
    </main>
  )
}
