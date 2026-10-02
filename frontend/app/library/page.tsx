import { SearchIcon } from "lucide-react"
import type { Metadata } from "next"

import { InputAction } from "@/components/input-action"
import { PreparationList } from "@/components/preparations/preparation-list"
import { PAGE_SIZE } from "@/constants/lists"
import { serverFetch } from "@/lib/server-api"
import type { PreparationSummary } from "@/types/preparation"

export const metadata: Metadata = { title: "Public library" }

export default async function LibraryPage({
  searchParams,
}: {
  searchParams: Promise<{ q?: string }>
}) {
  const q = (await searchParams).q?.trim() ?? ""
  const path = `/library/library?q=${encodeURIComponent(q)}`
  // The first page renders on the server; the rest load as the user scrolls.
  const first =
    (await serverFetch<PreparationSummary[]>(`${path}&limit=${PAGE_SIZE}`)) ??
    []

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

      <PreparationList
        path={path}
        initial={first}
        empty={
          <p className="py-16 text-center text-muted-foreground">
            {q ? "No matching preparations." : "No public preparations yet."}
          </p>
        }
      />
    </main>
  )
}
