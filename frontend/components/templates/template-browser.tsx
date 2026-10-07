import { SearchIcon } from "lucide-react"
import { getTranslations } from "next-intl/server"

import { InputAction } from "@/components/input-action"
import {
  type TemplateChoice,
  TemplateFilterBar,
} from "@/components/templates/template-filters"
import { TemplateList } from "@/components/templates/template-list"
import { MAX_TITLE_LENGTH } from "@/constants/limits"
import { PAGE_SIZE } from "@/constants/lists"
import { serverFetch } from "@/lib/server-api"
import type { TemplateFilters, TemplateSummary } from "@/types/superadmin"

export type TemplateSearchParams = {
  q?: string
  level?: string
  lang?: string | string[]
}

/** The templates searched and filtered like the old public library, on the page at `base` (the
 * address keeps the choices). `listPath` is the API list; rows open under `openBase` (by their
 * readable slug with `bySlug`, the public practice pages), and carry a "Use template" button for
 * `companyId`. Null when the list can't be read. */
export async function TemplateBrowser({
  base,
  listPath,
  params,
  openBase,
  companyId,
  bySlug,
}: {
  base: string
  listPath: string
  params: TemplateSearchParams
  openBase: string
  companyId?: string
  bySlug?: boolean
}) {
  const t = await getTranslations("templates")
  const filters = await serverFetch<TemplateFilters>(
    "/library/templates/filters"
  )

  if (!filters) {
    return null
  }

  const asked = [params.lang ?? []].flat()
  // Only what the API offers; anything else in the address is ignored.
  const choice: TemplateChoice = {
    q: params.q?.trim() ?? "",
    level: filters.levels.find((level) => level === params.level) ?? null,
    languages: filters.languages.filter((code) => asked.includes(code)),
  }
  const query = new URLSearchParams()

  if (choice.q) {
    query.set("q", choice.q)
  }

  if (choice.level) {
    query.set("level", choice.level)
  }

  choice.languages.forEach((language) => query.append("language", language))

  const path = `${listPath}?${query}`
  const narrowed = Boolean(choice.q || choice.level || choice.languages.length)
  // The first page renders on the server; the rest load as the user scrolls.
  const first = await serverFetch<TemplateSummary[]>(
    `${path}&limit=${PAGE_SIZE}`
  )

  if (!first) {
    return null
  }

  return (
    <>
      <form action={base} className="flex">
        <InputAction
          maxLength={MAX_TITLE_LENGTH}
          name="q"
          defaultValue={choice.q}
          placeholder={t("search")}
          aria-label={t("search")}
          action={t("searchAction")}
          icon={<SearchIcon className="size-5" />}
          // The level and languages sit inside the field, before its button.
          addon={
            <TemplateFilterBar base={base} filters={filters} current={choice} />
          }
        />
        {/* A new search keeps the level and languages. */}
        {choice.level && (
          <input type="hidden" name="level" value={choice.level} />
        )}
        {choice.languages.map((language) => (
          <input key={language} type="hidden" name="lang" value={language} />
        ))}
      </form>

      <TemplateList
        path={path}
        initial={first}
        empty={narrowed ? t("noMatches") : t("empty")}
        openBase={openBase}
        companyId={companyId}
        bySlug={bySlug}
      />
    </>
  )
}
