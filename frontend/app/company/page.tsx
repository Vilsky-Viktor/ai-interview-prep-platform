import type { Metadata } from "next"
import { cookies } from "next/headers"

import { CreateCompany } from "@/components/company/create-company"
import { CompanyList } from "@/components/company/company-list"
import { SignInPrompt } from "@/components/sign-in-prompt"
import { TOKEN_COOKIE } from "@/constants/auth"
import { PAGE_SIZE } from "@/constants/lists"
import { serverFetch } from "@/lib/server-api"
import type { Company } from "@/types/company"

export const metadata: Metadata = { title: "Company" }

export default async function CompanyPage() {
  const signedIn = (await cookies()).has(TOKEN_COOKIE)
  // The first page renders on the server; the rest load as the user scrolls.
  const companies = signedIn
    ? await serverFetch<Company[]>(`/companies/companies?limit=${PAGE_SIZE}`)
    : null

  return (
    <main className="mx-auto max-w-5xl space-y-8 px-6 py-12">
      <div className="flex items-center justify-between gap-4">
        <h1 className="font-heading text-3xl font-medium tracking-tight">
          Companies
        </h1>
        {signedIn && <CreateCompany />}
      </div>

      {!signedIn && (
        <SignInPrompt message="Sign in to create or open a company." />
      )}

      {signedIn && <CompanyList initial={companies ?? []} />}
    </main>
  )
}
