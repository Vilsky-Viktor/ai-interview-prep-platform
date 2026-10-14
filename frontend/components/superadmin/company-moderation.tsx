"use client"

import { SearchIcon } from "lucide-react"
import { useTranslations } from "next-intl"
import { useState } from "react"
import { toast } from "sonner"

import { InputAction } from "@/components/input-action"
import { CompanyModerationRow } from "@/components/superadmin/company-moderation-row"
import { LIST_BOX } from "@/constants/lists"
import { apiErrorMessage, apiFetch } from "@/lib/api"
import type { SuperadminCompany } from "@/types/superadmin"

const PATH = "/companies/superadmin/companies"

/** The admin zone's companies tab: finds companies by name, newest first, to suspend, rename or
 * delete one that impersonates another or abuses prepza. */
export function CompanyModeration({
  initial,
}: {
  initial: SuperadminCompany[]
}) {
  const t = useTranslations("superadmin")
  const [query, setQuery] = useState("")
  const [shown, setShown] = useState(initial)
  const [searching, setSearching] = useState(false)

  async function load(q: string) {
    setSearching(true)

    try {
      setShown(
        await apiFetch<SuperadminCompany[]>(
          `${PATH}?q=${encodeURIComponent(q)}`
        )
      )
    } catch (error) {
      toast.error(apiErrorMessage(error, t("actionFailed")))
    } finally {
      setSearching(false)
    }
  }

  return (
    <div className="space-y-8">
      <form
        onSubmit={(event) => {
          event.preventDefault()
          void load(query)
        }}
        className="flex"
      >
        <InputAction
          maxLength={200}
          placeholder={t("companySearch")}
          aria-label={t("companySearch")}
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          action={t("emailSearchAction")}
          icon={<SearchIcon className="size-5" />}
          disabled={searching}
        />
      </form>
      {shown.length === 0 && (
        <p className="py-10 text-center text-muted-foreground">
          {t("companiesNotFound")}
        </p>
      )}
      {shown.length > 0 && (
        <ul className={LIST_BOX}>
          {shown.map((company) => (
            <CompanyModerationRow
              key={company.id}
              company={company}
              onChanged={() => load(query)}
            />
          ))}
        </ul>
      )}
    </div>
  )
}
