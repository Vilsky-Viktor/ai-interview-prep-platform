"use client"

import { SearchIcon } from "lucide-react"
import { useTranslations } from "next-intl"
import { useState } from "react"
import { toast } from "sonner"

import { InputAction } from "@/components/input-action"
import { AccountEmails } from "@/components/superadmin/account-emails"
import { CompanyOptOuts } from "@/components/superadmin/company-opt-outs"
import { apiErrorMessage } from "@/lib/api"
import { findAddress } from "@/lib/superadmin-emails"
import type { CandidateOptOuts, EmailLookup } from "@/types/superadmin"

type Found = { email: string; lookup: EmailLookup; optOuts: CandidateOptOuts }

/** Finds an address: its prepza account's email settings, and the companies that invited it.
 * The address stays out of the page's address. */
export function EmailLookupView() {
  const t = useTranslations("superadmin")
  const [email, setEmail] = useState("")
  const [found, setFound] = useState<Found>()
  const [searching, setSearching] = useState(false)

  async function search(event: React.FormEvent) {
    event.preventDefault()
    setSearching(true)

    try {
      setFound({ email, ...(await findAddress(email)) })
    } catch (error) {
      toast.error(apiErrorMessage(error, t("actionFailed")))
    } finally {
      setSearching(false)
    }
  }

  return (
    <div className="space-y-8">
      <form onSubmit={search} className="flex">
        <InputAction
          required
          type="email"
          maxLength={320}
          placeholder={t("emailSearch")}
          aria-label={t("emailSearch")}
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          action={t("emailSearchAction")}
          icon={<SearchIcon className="size-5" />}
          disabled={searching}
        />
      </form>
      {found ? (
        // A new search starts both sections afresh.
        <div key={JSON.stringify(found)} className="space-y-8">
          <AccountEmails account={found.lookup.account ?? null} />
          <CompanyOptOuts email={found.email} initial={found.optOuts} />
        </div>
      ) : (
        <p className="py-10 text-center text-muted-foreground">
          {t("emailsIntro")}
        </p>
      )}
    </div>
  )
}
