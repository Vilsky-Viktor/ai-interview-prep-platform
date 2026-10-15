import { CompanyModeration } from "@/components/superadmin/company-moderation"
import { SuperadminHeader } from "@/components/superadmin/superadmin-header"
import type { SuperadminCompany } from "@/types/superadmin"
import { serverFetch } from "@/lib/server-api"
import { translatedTitle } from "@/lib/site"

export const generateMetadata = () => translatedTitle("superadmin", "zone")

/** The admin zone's companies tab: finds a company to suspend, rename or delete (impersonation,
 * abuse). The API answers superadmins only. */
export default async function CompaniesPage() {
  // The newest companies, before any search.
  const newest = await serverFetch<SuperadminCompany[]>(
    "/companies/superadmin/companies?q="
  )

  return (
    <main className="mx-auto max-w-5xl space-y-8 px-6 py-12">
      <SuperadminHeader current="companies" />
      <CompanyModeration initial={newest ?? []} />
    </main>
  )
}
