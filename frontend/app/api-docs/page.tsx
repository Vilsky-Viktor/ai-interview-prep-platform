import { notFound } from "next/navigation"
import { getLocale, getTranslations } from "next-intl/server"

import { Fields } from "@/components/api-docs/fields"
import { Operation } from "@/components/api-docs/operation"
import { RichText } from "@/components/api-docs/rich-text"
import { CopyValue } from "@/components/copy-field"
import { DEFAULT_LOCALE } from "@/constants/i18n"
import { fieldsOf, operationsOf, schemasOf } from "@/lib/openapi"
import { serverFetch } from "@/lib/server-api"
import { pageMetadata } from "@/lib/site"
import type { OpenApi } from "@/types/openapi"

export async function generateMetadata() {
  const t = await getTranslations("apiDocs")

  return pageMetadata(t("title"), t("intro"), "/api-docs")
}

/** The public API's reference, read from the API's own description, so it always matches it:
 * how to sign in, its routes, its web hook and the objects they return. English only, like
 * the legal pages. */
export default async function ApiDocsPage() {
  const t = await getTranslations("apiDocs")
  const locale = await getLocale()
  const spec = await serverFetch<OpenApi>("/v1/openapi.json")

  if (!spec) {
    notFound()
  }

  const base = spec.servers?.[0]?.url ?? ""

  return (
    <main className="mx-auto max-w-5xl space-y-12 px-6 py-12">
      <header className="space-y-4">
        {/* An acronym: its capitals stay, though titles are lowercase. */}
        <h1 className="font-heading text-4xl font-medium tracking-tight normal-case">
          {t("title")}
        </h1>
        {locale !== DEFAULT_LOCALE && (
          <p className="text-sm text-muted-foreground">{t("englishOnly")}</p>
        )}
      </header>
      <div lang="en" dir="ltr" className="space-y-12">
        {spec.info.description && <RichText text={spec.info.description} />}
        <Section title={t("baseUrl")}>
          <CopyValue
            value={base}
            label={t("copyBaseUrl")}
            copied={t("baseUrlCopied")}
          />
        </Section>
        <Section title={t("endpoints")}>
          {operationsOf(spec.paths).map((item) => (
            <Operation
              key={`${item.method} ${item.path}`}
              spec={spec}
              {...item}
            />
          ))}
        </Section>
        {spec.webhooks && (
          <Section title={t("webhooks")}>
            {operationsOf(spec.webhooks).map((item) => (
              <Operation key={item.path} spec={spec} {...item} />
            ))}
          </Section>
        )}
        <Section title={t("objects")}>
          {schemasOf(spec).map(([name, schema]) => (
            <article key={name} id={name} className="scroll-mt-20 space-y-3">
              <h3 className="font-mono text-xl font-medium normal-case">
                {name}
              </h3>
              {schema.description && <RichText text={schema.description} />}
              <Fields fields={fieldsOf(spec, schema)} />
            </article>
          ))}
        </Section>
      </div>
    </main>
  )
}

function Section({
  title,
  children,
}: {
  title: string
  children: React.ReactNode
}) {
  return (
    <section className="space-y-6">
      <h2 className="font-heading text-2xl font-medium">{title}</h2>
      {children}
    </section>
  )
}
