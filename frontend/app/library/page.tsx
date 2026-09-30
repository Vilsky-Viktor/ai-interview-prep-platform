import { SearchIcon } from "lucide-react"
import type { Metadata } from "next"

import { InputAction } from "@/components/input-action"
import { PreparationList } from "@/components/preparations/preparation-list"
import { serverFetch } from "@/lib/server-api"
import type { PreparationSummary } from "@/types/preparation"

export const metadata: Metadata = { title: "Public library" }

export default async function LibraryPage({
  searchParams,
}: {
  searchParams: Promise<{ q?: string }>
}) {
  const q = (await searchParams).q?.trim() ?? ""
  const results =
    (await serverFetch<PreparationSummary[]>(
      `/library/library?q=${encodeURIComponent(q)}`
    )) ?? []

  return (
    <main className="mx-auto max-w-5xl space-y-8 px-6 py-12">
      <h1 className="font-heading text-3xl font-medium tracking-tight">
        Public library
      </h1>

      <form action="/library" className="flex">
        <InputAction
          name="q"
          defaultValue={q}
          placeholder="Search titles and topics"
          aria-label="Search titles and topics"
          action="Search"
          icon={<SearchIcon className="size-5" />}
        />
      </form>

      {results.length === 0 ? (
        <p className="py-16 text-center text-muted-foreground">
          {q
            ? "No matching preparations."
            : "No public preparations yet."}
        </p>
      ) : (
        <PreparationList preparations={results} />
      )}
    </main>
  )
}
