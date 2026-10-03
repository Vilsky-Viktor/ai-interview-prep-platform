import { ChevronDownIcon } from "lucide-react"
import { getTranslations } from "next-intl/server"

import { HelpChat } from "@/components/help-chat"
import { serverFetch } from "@/lib/server-api"
import { pageMetadata } from "@/lib/site"
import type { FaqItem } from "@/types/help"

export async function generateMetadata() {
  const t = await getTranslations("faq")

  return pageMetadata(t("title"), t("intro"), "/faq")
}

export default async function FaqPage() {
  const t = await getTranslations("faq")
  // The questions come from the rounds service in the page's language, with today's prices.
  const items = (await serverFetch<FaqItem[]>("/rounds/help/faq")) ?? []
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
      <HelpChat />
    </main>
  )
}
