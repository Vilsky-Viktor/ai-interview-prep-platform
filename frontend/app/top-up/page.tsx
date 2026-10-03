import { cookies } from "next/headers"
import Link from "next/link"
import { getTranslations } from "next-intl/server"

import { BalanceRow } from "@/components/billing/balance-row"
import { SignInPrompt } from "@/components/sign-in-prompt"
import { Button } from "@/components/ui/button"
import { TOKEN_COOKIE } from "@/constants/auth"
import { serverFetch } from "@/lib/server-api"
import { translatedTitle } from "@/lib/site"
import type { Balance, Catalog } from "@/types/billing"
import type { CompanyBalance } from "@/types/company"

export const generateMetadata = () => translatedTitle("topUp", "title")

function SectionTitle({ title, note }: { title: string; note: string }) {
  return (
    <div className="space-y-1">
      <h2 className="font-heading text-2xl font-medium">{title}</h2>
      <p className="text-base text-muted-foreground">{note}</p>
    </div>
  )
}

export default async function TopUpPage() {
  const signedIn = (await cookies()).has(TOKEN_COOKIE)
  const t = await getTranslations("topUp")
  const [catalog, balance, companies] = signedIn
    ? await Promise.all([
        serverFetch<Catalog>("/billing/catalog"),
        serverFetch<Balance>("/billing/me"),
        serverFetch<CompanyBalance[]>("/companies/companies/credits?limit=100"),
      ])
    : [null, null, null]

  return (
    <main className="mx-auto max-w-5xl space-y-12 px-6 py-12">
      <div className="space-y-2">
        <div className="flex items-center justify-between gap-4">
          <h1 className="font-heading text-4xl font-medium tracking-tight">
            {t("title")}
          </h1>
          <Button
            variant="outline"
            className="h-12 px-6 text-base"
            render={<Link href="/pricing" />}
            nativeButton={false}
          >
            {t("pricing")}
          </Button>
        </div>
        <p className="text-base text-muted-foreground">{t("intro")}</p>
      </div>

      {!signedIn && <SignInPrompt message={t("signIn")} />}

      {catalog && balance && (
        <section className="space-y-4">
          <SectionTitle title={t("personal")} note={t("personalNote")} />
          <div className="rounded-2xl border">
            <BalanceRow
              catalog={catalog}
              name={t("yours")}
              available={balance.available}
            />
          </div>
        </section>
      )}

      {catalog && companies && companies.length > 0 && (
        <section className="space-y-4">
          <SectionTitle title={t("companies")} note={t("companiesNote")} />
          <div className="divide-y rounded-2xl border">
            {companies.map((company) => (
              <BalanceRow
                key={company.id}
                catalog={catalog}
                name={company.name}
                available={company.available}
                companyId={company.id}
              />
            ))}
          </div>
        </section>
      )}
    </main>
  )
}
