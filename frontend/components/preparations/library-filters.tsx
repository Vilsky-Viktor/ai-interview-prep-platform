"use client"

import { ChevronDownIcon } from "lucide-react"
import { useRouter } from "next/navigation"
import { useTranslations } from "next-intl"

import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuRadioGroup,
  DropdownMenuRadioItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { LANGUAGE_NAMES, type Locale } from "@/constants/i18n"
import { isLocale } from "@/lib/locale"
import type { LibraryFilters, LibrarySort } from "@/types/preparation"

// "Any level" in the level menu; levels themselves come from the API.
const ANY = "any"
const TRIGGER = "h-10 gap-2 px-4"

export type LibraryChoice = {
  q: string
  level: string | null
  languages: string[]
  sort: LibrarySort
}

/** The address of the library with these choices; the server renders it already filtered. */
function libraryHref({ q, level, languages, sort }: LibraryChoice) {
  const params = new URLSearchParams()

  if (q) {
    params.set("q", q)
  }

  if (level) {
    params.set("level", level)
  }

  languages.forEach((language) => params.append("lang", language))
  params.set("sort", sort)

  return `/library?${params}`
}

function languageName(code: string) {
  return isLocale(code) ? LANGUAGE_NAMES[code as Locale] : code
}

/** The library's level, languages and order; what can be chosen comes from the API. */
export function LibraryFilterBar({
  filters,
  current,
}: {
  filters: LibraryFilters
  current: LibraryChoice
}) {
  const t = useTranslations("library")
  const levels = useTranslations("levels")
  const router = useRouter()

  function choose(change: Partial<LibraryChoice>) {
    router.replace(libraryHref({ ...current, ...change }), { scroll: false })
  }

  function toggle(language: string, checked: boolean) {
    const languages = checked
      ? [...current.languages, language]
      : current.languages.filter((item) => item !== language)
    // In the API's order, so the address is the same whichever was ticked first.
    choose({
      languages: filters.languages.filter((item) => languages.includes(item)),
    })
  }

  const languagesLabel =
    current.languages.length <= 2
      ? current.languages.map(languageName).join(", ")
      : t("languages", { count: current.languages.length })

  return (
    <div className="flex flex-wrap items-center gap-3">
      <DropdownMenu>
        <DropdownMenuTrigger
          render={<Button variant="outline" className={TRIGGER} />}
        >
          {t("level", {
            level: current.level ? levels(current.level) : t("anyLevel"),
          })}
          <ChevronDownIcon className="text-muted-foreground" />
        </DropdownMenuTrigger>
        <DropdownMenuContent align="start" className="w-48 p-2">
          <DropdownMenuRadioGroup
            value={current.level ?? ANY}
            onValueChange={(level) =>
              choose({ level: level === ANY ? null : level })
            }
          >
            <DropdownMenuRadioItem value={ANY} className="px-3 py-2 lowercase">
              {t("anyLevel")}
            </DropdownMenuRadioItem>
            {filters.levels.map((level) => (
              <DropdownMenuRadioItem
                key={level}
                value={level}
                className="px-3 py-2 lowercase"
              >
                {levels(level)}
              </DropdownMenuRadioItem>
            ))}
          </DropdownMenuRadioGroup>
        </DropdownMenuContent>
      </DropdownMenu>

      <DropdownMenu>
        <DropdownMenuTrigger
          render={
            <Button variant="outline" className={`${TRIGGER} normal-case`} />
          }
        >
          {languagesLabel}
          <ChevronDownIcon className="text-muted-foreground" />
        </DropdownMenuTrigger>
        <DropdownMenuContent
          align="start"
          className="max-h-80 w-56 overflow-y-auto p-2"
        >
          {filters.languages.map((language) => {
            const checked = current.languages.includes(language)

            return (
              <DropdownMenuCheckboxItem
                key={language}
                lang={language}
                checked={checked}
                // At least one language stays: none would mean the defaults again.
                disabled={checked && current.languages.length === 1}
                onCheckedChange={(next) => toggle(language, next)}
                className="px-3 py-2"
              >
                {languageName(language)}
              </DropdownMenuCheckboxItem>
            )
          })}
        </DropdownMenuContent>
      </DropdownMenu>

      <DropdownMenu>
        <DropdownMenuTrigger
          render={<Button variant="outline" className={`${TRIGGER} ms-auto`} />}
        >
          {t("sortBy", { sort: t(`sort.${current.sort}`) })}
          <ChevronDownIcon className="text-muted-foreground" />
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="w-48 p-2">
          <DropdownMenuRadioGroup
            value={current.sort}
            onValueChange={(sort) => choose({ sort: sort as LibrarySort })}
          >
            {filters.sorts.map((sort) => (
              <DropdownMenuRadioItem
                key={sort}
                value={sort}
                className="px-3 py-2 lowercase"
              >
                {t(`sort.${sort}`)}
              </DropdownMenuRadioItem>
            ))}
          </DropdownMenuRadioGroup>
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  )
}
