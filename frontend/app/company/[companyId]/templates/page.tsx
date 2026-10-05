import { TriangleAlertIcon } from "lucide-react"
import { cookies } from "next/headers"
import { redirect } from "next/navigation"
import { getTranslations } from "next-intl/server"

import { CompanyHeader } from "@/components/company/company-header"
import { SignInPrompt } from "@/components/sign-in-prompt"
import {
  TemplateBrowser,
  type TemplateSearchParams,
} from "@/components/templates/template-browser"
import { TOKEN_COOKIE } from "@/constants/auth"
import { serverFetch } from "@/lib/server-api"
import { translatedTitle } from "@/lib/site"
import type { Company } from "@/types/company"

export const generateMetadata = () => translatedTitle("templates", "title")

/** Templates a company starts a test from, searched like the superadmin's list; using one copies
 * it into the company's own test. */
export default async function CompanyTemplatesPage({
  params,
  searchParams,
}: {
  params: Promise<{ companyId: string }>
  searchParams: Promise<TemplateSearchParams>
}) {
  const { companyId } = await params
  const t = await getTranslations("templates")
  const companyText = await getTranslations("company")
  const signedIn = (await cookies()).has(TOKEN_COOKIE)
  const company = signedIn
    ? await serverFetch<Company>(`/companies/companies/${companyId}`)
    : null

  if (!signedIn) {
    return (
      <main className="mx-auto max-w-5xl px-6 py-12">
        <SignInPrompt message={companyText("signInInterviews")} />
      </main>
    )
  }

  if (!company) {
    redirect("/company")
  }

  const browser = await TemplateBrowser({
    base: `/company/${companyId}/templates`,
    listPath: "/library/templates",
    params: await searchParams,
    openBase: `/company/${companyId}/templates`,
    companyId,
  })

  return (
    <main className="mx-auto max-w-5xl space-y-8 px-6 py-12">
      <CompanyHeader
        companyId={companyId}
        name={company.name}
        logoUrl={company.logo_url ?? null}
        verifiedDomain={company.verified_domain ?? null}
        websiteDomain={company.website_domain ?? null}
        current="templates"
      />
      {/* Templates are practiced by talents, so they're no secret: for trying prepza only. */}
      <div className="flex items-center gap-4 rounded-2xl bg-muted p-5 text-base">
        <TriangleAlertIcon
          aria-hidden
          className="size-7 shrink-0 text-amber-600 dark:text-amber-400"
        />
        <p className="text-muted-foreground">
          <span className="font-medium text-foreground">
            {t("warningTitle")}
          </span>{" "}
          {t("warning")}
        </p>
      </div>
      {browser}
    </main>
  )
}
