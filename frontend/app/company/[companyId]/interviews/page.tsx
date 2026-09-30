import { PlusIcon, UsersIcon } from "lucide-react"
import type { Metadata } from "next"
import { cookies } from "next/headers"
import Link from "next/link"
import { redirect } from "next/navigation"

import { CompanyHeader } from "@/components/company/company-header"
import { SignInPrompt } from "@/components/sign-in-prompt"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { TOKEN_COOKIE } from "@/constants/auth"
import { MODE_LABELS } from "@/constants/rounds"
import { formatDate } from "@/lib/format"
import { serverFetch } from "@/lib/server-api"
import type { Company, Interview } from "@/types/company"

export const metadata: Metadata = { title: "Interviews" }

export default async function InterviewsPage({
  params,
}: {
  params: Promise<{ companyId: string }>
}) {
  const { companyId } = await params
  const signedIn = (await cookies()).has(TOKEN_COOKIE)
  const company = signedIn
    ? await serverFetch<Company>(`/companies/companies/${companyId}`)
    : null
  const interviews = company
    ? await serverFetch<Interview[]>(
        `/companies/interviews?company_id=${companyId}`
      )
    : null

  if (!signedIn) {
    return (
      <main className="mx-auto max-w-5xl px-6 py-12">
        <SignInPrompt message="Sign in to see company interviews." />
      </main>
    )
  }

  if (!company) {
    redirect("/company")
  }

  return (
    <main className="mx-auto max-w-5xl space-y-8 px-6 py-12">
      <CompanyHeader
        companyId={companyId}
        name={company.name}
        current="interviews"
        action={
          <Button
            render={<Link href={`/company/${companyId}/interviews/new`} />}
            nativeButton={false}
            size="icon"
            className="size-14 rounded-full"
            aria-label="New interview"
          >
            <PlusIcon className="size-6" />
          </Button>
        }
      />

      {interviews?.length === 0 && (
        <p className="py-16 text-center text-muted-foreground">
          No interviews yet. Create your first one.
        </p>
      )}

      {interviews && interviews.length > 0 && (
        <ul className="divide-y rounded-2xl border">
          {interviews.map((interview) => (
            <li key={interview.id}>
              <Link
                href={`/company/${companyId}/interviews/${interview.id}`}
                className="flex items-center justify-between gap-4 p-6 transition-colors hover:bg-muted/50"
              >
                <span className="space-y-1">
                  <span className="block text-lg font-medium">
                    {interview.title ?? "Generating…"}
                  </span>
                  <span className="block text-sm text-muted-foreground">
                    {formatDate(interview.created_at)}
                  </span>
                </span>
                <span className="flex shrink-0 items-center gap-4">
                  <span
                    className="flex items-center gap-1.5 text-sm text-muted-foreground tabular-nums"
                    aria-label={`${interview.candidate_count} candidates`}
                  >
                    <UsersIcon aria-hidden className="size-5" />
                    {interview.candidate_count}
                  </span>
                  <Badge
                    variant="secondary"
                    className="h-7 px-3 text-sm font-light"
                  >
                    {MODE_LABELS[interview.mode]}
                  </Badge>
                </span>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </main>
  )
}
