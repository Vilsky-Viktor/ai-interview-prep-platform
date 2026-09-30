import { MessagesSquareIcon, UserRoundIcon } from "lucide-react"
import type { Metadata } from "next"
import { cookies } from "next/headers"
import Link from "next/link"

import { CreateCompany } from "@/components/company/create-company"
import { RemoveCompany } from "@/components/company/remove-company"
import { SignInPrompt } from "@/components/sign-in-prompt"
import { Badge } from "@/components/ui/badge"
import { TOKEN_COOKIE } from "@/constants/auth"
import { serverFetch } from "@/lib/server-api"
import type { Company } from "@/types/company"

export const metadata: Metadata = { title: "Company" }

export default async function CompanyPage() {
  const signedIn = (await cookies()).has(TOKEN_COOKIE)
  const companies = signedIn
    ? await serverFetch<Company[]>("/companies/companies")
    : null

  const items = companies ?? []

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

      {signedIn && (
        <ul className="divide-y rounded-2xl border">
          {items.length === 0 && (
            <li className="p-6 text-muted-foreground">No companies yet.</li>
          )}
          {items.map((company) => (
            <li key={company.id} className="flex items-center gap-2 pr-3">
              <Link
                href={`/company/${company.id}/interviews`}
                className="flex min-w-0 flex-1 items-center justify-between gap-4 p-6 transition-colors hover:bg-muted/50"
              >
                <span className="flex min-w-0 items-center gap-2">
                  <span className="text-xl font-medium">{company.name}</span>
                  {company.role === "owner" && (
                    <span
                      role="img"
                      aria-label="Owner"
                      className="text-muted-foreground"
                    >
                      <UserRoundIcon className="size-5" />
                    </span>
                  )}
                </span>
                <span className="flex shrink-0 items-center gap-4">
                  <span
                    className="flex items-center gap-1.5 text-sm text-muted-foreground tabular-nums"
                    aria-label={`${company.interview_count} interviews`}
                  >
                    <MessagesSquareIcon aria-hidden className="size-5" />
                    {company.interview_count}
                  </span>
                  {company.role !== "owner" && (
                    <Badge
                      variant="secondary"
                      className="h-7 px-3 text-sm font-light capitalize"
                    >
                      {company.role}
                    </Badge>
                  )}
                </span>
              </Link>
              {company.role === "owner" && (
                <RemoveCompany companyId={company.id} name={company.name} />
              )}
            </li>
          ))}
        </ul>
      )}
    </main>
  )
}
