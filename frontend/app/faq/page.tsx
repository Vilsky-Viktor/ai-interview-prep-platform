import { ChevronDownIcon } from "lucide-react"
import { getTranslations } from "next-intl/server"

import { FAQ_ITEMS } from "@/constants/faq"
import { LOCALES } from "@/constants/i18n"
import { serverFetch } from "@/lib/server-api"
import { pageMetadata } from "@/lib/site"
import type { Catalog } from "@/types/billing"

export async function generateMetadata() {
  const t = await getTranslations("faq")

  return pageMetadata(t("title"), t("intro"), "/faq")
}

export default async function FaqPage() {
  const t = await getTranslations("faq")
  // Prices come from billing, which decides them.
  const catalog = await serverFetch<Catalog>("/billing/catalog")
  const values = {
    count: LOCALES.length,
    kit: catalog?.kit_credits ?? "",
    welcome: catalog?.welcome_user ?? "",
    candidate: catalog?.candidate_credits ?? "",
    company: catalog?.welcome_company ?? "",
  }
  const items = FAQ_ITEMS.map((key) => ({
    key,
    question: t(`items.${key}.q`),
    answer: t(`items.${key}.a`, values),
  }))
  // FAQ structured data, so search engines can show the answers.
  const structured = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    mainEntity: items.map((item) => ({
      "@type": "Question",
      name: item.question,
      acceptedAnswer: { "@type": "Answer", text: item.answer },
    })),
  }

  return (
    <main className="mx-auto max-w-5xl space-y-10 px-6 py-12">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify(structured).replace(/</g, "\\u003c"),
        }}
      />
      <header className="space-y-4">
        <h1 className="font-heading text-4xl font-medium tracking-tight">
          {t("title")}
        </h1>
        <p className="text-base text-muted-foreground">{t("intro")}</p>
      </header>
      <div className="divide-y rounded-3xl bg-card shadow-sm ring-1 ring-foreground/5">
        {items.map((item) => (
          <details key={item.key} className="group px-6">
            <summary className="flex cursor-pointer list-none items-center justify-between gap-4 py-5 font-medium [&::-webkit-details-marker]:hidden">
              {item.question}
              <ChevronDownIcon className="size-5 shrink-0 text-muted-foreground transition-transform group-open:rotate-180" />
            </summary>
            <p className="pb-5 text-base leading-relaxed text-muted-foreground">
              {item.answer}
            </p>
          </details>
        ))}
      </div>
    </main>
  )
}
