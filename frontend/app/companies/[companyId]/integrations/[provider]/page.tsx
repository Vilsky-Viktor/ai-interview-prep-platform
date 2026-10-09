import { cookies } from "next/headers"
import { notFound, redirect } from "next/navigation"
import { getTranslations } from "next-intl/server"

import { BackLink } from "@/components/back-link"
import { AtsActions, AtsStatus } from "@/components/company/ats-connection"
import { AtsJobLinks } from "@/components/company/ats-job-links"
import { PageHeader } from "@/components/page-header"
import { SignInPrompt } from "@/components/sign-in-prompt"
import { ATS_PROVIDERS } from "@/constants/ats"
import { TOKEN_COOKIE } from "@/constants/auth"
import { serverFetch } from "@/lib/server-api"
import type {
  AtsIntegrations,
  AtsJobLink,
  Company,
  Interview,
} from "@/types/company"

type Params = Promise<{ companyId: string; provider: string }>

function providerOf(id: string) {
  return ATS_PROVIDERS.find((item) => item.id === id)
}

export const generateMetadata = async ({ params }: { params: Params }) => ({
  title: providerOf((await params).provider)?.name,
})

/** An ATS's own page, laid out like an interview's: back to the integrations tab, its status
 * and buttons, and once connected, its linked jobs with "Link a job" and Unlink; before, that it
 * isn't connected yet. */
export default async function AtsPage({ params }: { params: Params }) {
  const { companyId, provider: id } = await params
  const provider = providerOf(id)

  if (!provider) {
    notFound()
  }

  const signedIn = (await cookies()).has(TOKEN_COOKIE)
  const t = await getTranslations("company")
  const ats = await getTranslations("ats")
  const company = signedIn
    ? await serverFetch<Company>(`/companies/companies/${companyId}`)
    : null
  const [integrations, links, interviews] = company
    ? await Promise.all([
        serverFetch<AtsIntegrations>(
          `/ats/connections?company_id=${companyId}`
        ),
        serverFetch<AtsJobLink[]>(`/ats/links?company_id=${companyId}`),
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

  const connection =
    integrations.connections.find((item) => item.provider === provider.id) ??
    null
  const connected = connection?.status === "connected"

  return (
    <main className="mx-auto max-w-5xl space-y-8 px-6 py-12">
      <PageHeader
        back={
          <BackLink href={`/companies/${companyId}/integrations`} help="ats">
            {t("integrations")}
          </BackLink>
        }
        title={
          <div className="flex items-start justify-between gap-4">
            <div className="flex min-w-0 items-center gap-4">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={provider.logo}
                alt=""
                className="size-12 shrink-0 rounded-xl"
              />
              <div className="min-w-0 space-y-1">
                <div className="flex items-center gap-3">
                  <h1 className="font-heading text-3xl font-medium tracking-tight normal-case">
                    {provider.name}
                  </h1>
                  <AtsStatus connection={connection} />
                </div>
                {connection && (
                  <p className="text-base text-muted-foreground">
                    {connection.account}
                  </p>
                )}
              </div>
            </div>
            <AtsActions
              companyId={companyId}
              provider={provider}
              connection={connection}
              canEdit={company.can_edit}
            />
          </div>
        }
      />
      {connection ? (
        <AtsJobLinks
          companyId={companyId}
          provider={provider}
          links={(links ?? []).filter((item) => item.provider === provider.id)}
          interviews={(interviews ?? []).filter((item) => item.set_id)}
          canEdit={company.can_edit && connected}
        />
      ) : (
        <p className="rounded-2xl border p-6 text-muted-foreground">
          {ats("notConnected", { ats: provider.name })}
        </p>
      )}
    </main>
  )
}
