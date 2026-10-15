import { notFound } from "next/navigation"
import { getLocale, getTranslations } from "next-intl/server"

import { Fields } from "@/components/api-docs/fields"
import { Operation } from "@/components/api-docs/operation"
import { RichText } from "@/components/api-docs/rich-text"
import { CopyValue } from "@/components/copy-field"
import { TabNav } from "@/components/tab-nav"
import { JsonLd } from "@/components/json-ld"
import { DOC_TABS } from "@/constants/api-docs"
import { DEFAULT_LOCALE } from "@/constants/i18n"
import {
  descriptionTabs,
  fieldsOf,
  operationsOf,
  schemasOf,
} from "@/lib/openapi"
import { publicFetch } from "@/lib/server-api"
import { pageMetadata, previewImage, siteUrl } from "@/lib/site"
import { breadcrumbData, techArticleData } from "@/lib/structured-data"
import type { OpenApi } from "@/types/openapi"

export async function generateMetadata() {
  const t = await getTranslations("apiDocs")

  return pageMetadata(t("title"), t("description"), "/api-docs")
}

/** The developer docs, read from the API's own description, so they always match it: a tab for
 * the API (how to sign in, its routes), its web hooks, the SDK that embeds the interview, and
 * the objects they return. English only, like the legal pages. */
export default async function ApiDocsPage({
  searchParams,
}: {
  searchParams: Promise<{ tab?: string }>
}) {
  const t = await getTranslations("apiDocs")
  const locale = await getLocale()
  const spec = await publicFetch<OpenApi>("/v1/openapi.json", { locale: "en" })

  if (!spec) {
    notFound()
  }

  const { tab } = await searchParams
  const current = DOC_TABS.find((item) => item === tab) ?? "api"
  const texts = descriptionTabs(spec.info.description ?? "")
  const tabs = DOC_TABS.map((id) => ({
    id,
    href: id === "api" ? "/api-docs" : `/api-docs?tab=${id}`,
    label: id === "objects" ? t("objects") : t(`tabs.${id}`),
    // Acronyms keep their capitals in the lowercase tabs.
    keepCase: id === "api" || id === "sdk",
  }))

  const base = spec.servers?.[0]?.url ?? ""
  const site = siteUrl()

  return (
    <main className="mx-auto max-w-5xl space-y-12 px-6 py-12">
      <JsonLd
        data={[
          techArticleData(site, {
            title: t("title"),
            description: t("description"),
            path: "/api-docs",
            image: previewImage(t("title"))[0].url,
          }),
          breadcrumbData(site, [
            { name: "prepza", path: "/" },
            { name: t("title"), path: "/api-docs" },
          ]),
        ]}
      />
      <header className="space-y-4">
        <h1 className="font-heading text-4xl font-medium tracking-tight">
          {t("title")}
        </h1>
        {locale !== DEFAULT_LOCALE && (
          <p className="text-sm text-muted-foreground">{t("englishOnly")}</p>
        )}
      </header>
      <TabNav items={tabs} current={current} />
      <div lang="en" dir="ltr" className="space-y-12">
        {current === "api" && (
          <>
            {texts.api && <RichText text={texts.api} />}
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
          </>
        )}
        {current === "webhooks" && (
          <>
            {texts.webhooks && <RichText text={texts.webhooks} />}
            {spec.webhooks && (
              <Section title={t("webhooks")}>
                {operationsOf(spec.webhooks).map((item) => (
                  <Operation key={item.path} spec={spec} {...item} />
                ))}
              </Section>
            )}
          </>
        )}
        {current === "sdk" && texts.sdk && <RichText text={texts.sdk} />}
        {current === "objects" &&
          schemasOf(spec).map(([name, schema]) => (
            <article key={name} id={name} className="scroll-mt-20 space-y-3">
              <h3 className="font-mono text-xl font-medium normal-case">
                {name}
              </h3>
              {schema.description && <RichText text={schema.description} />}
              <Fields fields={fieldsOf(spec, schema)} />
            </article>
          ))}
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
