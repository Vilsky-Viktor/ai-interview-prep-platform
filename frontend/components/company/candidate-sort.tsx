"use client"

import { ChevronDownIcon } from "lucide-react"
import { usePathname, useRouter, useSearchParams } from "next/navigation"
import { useTranslations } from "next-intl"

import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuRadioGroup,
  DropdownMenuRadioItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { CANDIDATE_SORTS, type CandidateSort } from "@/constants/interviews"

/** Chooses how the candidates are listed; the choice lives in the address, so the server
 * renders the first page in that order. */
export function CandidateSortMenu({ current }: { current: CandidateSort }) {
  const t = useTranslations("candidates")
  const router = useRouter()
  const pathname = usePathname()
  const searchParams = useSearchParams()

  // A new order keeps the search and the status filter.
  function choose(sort: string) {
    const params = new URLSearchParams(searchParams)
    params.set("sort", sort)
    router.replace(`${pathname}?${params}`, { scroll: false })
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger
        render={
          <Button
            type="button"
            variant="ghost"
            className="h-10 shrink-0 gap-1.5 px-3 text-sm"
          />
        }
      >
        {t("sortBy", { sort: t(`sort.${current}`) })}
        <ChevronDownIcon className="text-muted-foreground" />
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-48 p-2">
        <DropdownMenuRadioGroup value={current} onValueChange={choose}>
          {CANDIDATE_SORTS.map((sort) => (
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
  )
}
