"use client"

import { ArrowDownWideNarrowIcon, ChevronDownIcon } from "lucide-react"
import { usePathname, useRouter } from "next/navigation"
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

  return (
    <DropdownMenu>
      <DropdownMenuTrigger
        render={<Button variant="outline" className="h-10 gap-2 px-4" />}
      >
        <ArrowDownWideNarrowIcon />
        {t("sortBy", { sort: t(`sort.${current}`) })}
        <ChevronDownIcon className="text-muted-foreground" />
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-48 p-2">
        <DropdownMenuRadioGroup
          value={current}
          onValueChange={(sort) =>
            router.replace(`${pathname}?tab=candidates&sort=${sort}`, {
              scroll: false,
            })
          }
        >
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
