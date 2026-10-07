import { cookies } from "next/headers"
import { notFound, redirect } from "next/navigation"
import { getTranslations } from "next-intl/server"

import { BackLink } from "@/components/back-link"
import {
  WorkableActions,
  WorkableStatus,
} from "@/components/company/ats-connection"
import { AtsJobLinks } from "@/components/company/ats-job-links"
import { PageHeader } from "@/components/page-header"
import { SignInPrompt } from "@/components/sign-in-prompt"
import { TOKEN_COOKIE } from "@/constants/auth"
import { serverFetch } from "@/lib/server-api"
import type {
  AtsIntegrations,
  AtsJobLink,
  Company,
  Interview,
} from "@/types/company"

export const generateMetadata = () => ({ title: "Workable" })

/** Workable's own page, laid out like an interview's: back to the ATS tab, its status and
 * buttons, and once connected, its linked jobs with "Link a job" and Unlink. */
export default async function WorkablePage({
  params,
}: {
  params: Promise<{ companyId: string }>
}) {
  const { companyId } = await params
  const signedIn = (await cookies()).has(TOKEN_COOKIE)
  const t = await getTranslations("company")
  const company = signedIn
    ? await serverFetch<Company>(`/companies/companies/${companyId}`)
    : null
  const [integrations, links, interviews] = company
    ? await Promise.all([
        serverFetch<AtsIntegrations>(`/companies/ats?company_id=${companyId}`),
        serverFetch<AtsJobLink[]>(
          `/companies/ats/links?company_id=${companyId}`
        ),
        serverFetch<Interview[]>(
          `/companies/interviews?company_id=${companyId}&limit=100`
        ),
      ])
    : [null, null, null]

  if (!signedIn) {
    return (
      <main className="mx-auto max-w-5xl px-6 py-12">
        <SignInPrompt />
      </main>
    )
  }

  if (!company) {
    redirect("/companies")
  }

  if (!integrations?.available) {
    notFound()
  }

  const workable =
    integrations.connections.find((item) => item.provider === "workable") ??
    null

  return (
    <main className="mx-auto max-w-5xl space-y-8 px-6 py-12">
      <PageHeader
        back={
          <BackLink href={`/companies/${companyId}/integrations`}>
            {t("integrations")}
          </BackLink>
        }
        title={
          <div className="flex items-start justify-between gap-4">
            <div className="flex min-w-0 items-center gap-4">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src="/ats/workable.svg"
                alt=""
                className="size-12 shrink-0 rounded-xl"
              />
              <div className="min-w-0 space-y-1">
                <div className="flex items-center gap-3">
                  <h1 className="font-heading text-3xl font-medium tracking-tight normal-case">
                    Workable
                  </h1>
                  <WorkableStatus connection={workable} />
                </div>
                {workable && (
                  <p className="text-base text-muted-foreground">
                    {workable.account}
                  </p>
                )}
              </div>
            </div>
            <WorkableActions
              companyId={companyId}
              connection={workable}
              canEdit={company.can_edit}
            />
          </div>
        }
      />
      {workable && (
        <AtsJobLinks
          companyId={companyId}
          links={links ?? []}
          interviews={(interviews ?? []).filter((item) => item.set_id)}
          canEdit={company.can_edit && workable.status === "connected"}
        />
      )}
    </main>
  )
}
