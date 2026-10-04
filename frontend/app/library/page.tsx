import { SearchIcon } from "lucide-react"
import type { Metadata } from "next"
import { getTranslations } from "next-intl/server"

import { InputAction } from "@/components/input-action"
import {
  type LibraryChoice,
  LibraryFilterBar,
} from "@/components/preparations/library-filters"
import { PreparationList } from "@/components/preparations/preparation-list"
import { MAX_SEARCH_LENGTH } from "@/constants/limits"
import { PAGE_SIZE } from "@/constants/lists"
import { serverFetch } from "@/lib/server-api"
import type { LibraryFilters, PreparationSummary } from "@/types/preparation"

export async function generateMetadata(): Promise<Metadata> {
  const t = await getTranslations("library")

  return { title: t("title") }
}

type SearchParams = {
  q?: string
  level?: string
  lang?: string | string[]
  sort?: string
}

/** The reader's choices from the address, or the API's defaults where there are none (or
 * they're not offered). */
function readChoice(
  params: SearchParams,
  filters: LibraryFilters
): LibraryChoice {
  const asked = [params.lang ?? []].flat()
  const languages = filters.languages.filter((code) => asked.includes(code))

  return {
    q: params.q?.trim() ?? "",
    level: filters.levels.find((level) => level === params.level) ?? null,
    languages: languages.length > 0 ? languages : filters.default_languages,
    sort:
      filters.sorts.find((sort) => sort === params.sort) ??
      filters.default_sort,
  }
}

export default async function LibraryPage({
  searchParams,
}: {
  searchParams: Promise<SearchParams>
}) {
  const t = await getTranslations("library")
  const filters = await serverFetch<LibraryFilters>("/library/library/filters")
  const choice = filters ? readChoice(await searchParams, filters) : null
  const query = new URLSearchParams({ q: choice?.q ?? "" })

  if (choice) {
    if (choice.level) {
      query.set("level", choice.level)
    }

    choice.languages.forEach((language) => query.append("language", language))
    query.set("sort", choice.sort)
  }

  const path = `/library/library?${query}`
  // Narrowed by the reader, so an empty list means nothing matches, not an empty library.
  const narrowed = Boolean(
    choice &&
    filters &&
    (choice.q ||
      choice.level ||
      choice.languages.join() !== filters.default_languages.join())
  )
  // The first page renders on the server; the rest load as the user scrolls.
  const first =
    (await serverFetch<PreparationSummary[]>(`${path}&limit=${PAGE_SIZE}`)) ??
    []

  return (
    <main className="mx-auto max-w-5xl space-y-8 px-6 py-12">
      <h1 className="font-heading text-3xl font-medium tracking-tight">
        {t("title")}
      </h1>

      <div className="space-y-4">
        <form action="/library" className="flex">
          <InputAction
            maxLength={MAX_SEARCH_LENGTH}
            name="q"
            defaultValue={choice?.q}
            placeholder={t("search")}
            aria-label={t("search")}
            action={t("searchAction")}
            icon={<SearchIcon className="size-5" />}
          />
          {/* A new search keeps the level, languages and order. */}
          {choice?.level && (
            <input type="hidden" name="level" value={choice.level} />
          )}
          {choice?.languages.map((language) => (
            <input key={language} type="hidden" name="lang" value={language} />
          ))}
          {choice && <input type="hidden" name="sort" value={choice.sort} />}
        </form>
        {filters && choice && (
          <LibraryFilterBar filters={filters} current={choice} />
        )}
      </div>

      <PreparationList
        path={path}
        initial={first}
        empty={
          <p className="py-16 text-center text-muted-foreground">
            {narrowed ? t("noMatches") : t("empty")}
          </p>
        }
      />
    </main>
  )
}
