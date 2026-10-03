import { getLocale, getTranslations } from "next-intl/server"

import { DEFAULT_LOCALE } from "@/constants/i18n"
import { LEGAL_UPDATED, type LegalSection } from "@/constants/legal"

/** The privacy policy and terms, from their sections in constants. English only: they're legal
texts, and a translation would need its own legal review. */
export async function LegalPage({
  title,
  intro,
  sections,
}: {
  title: string
  intro: string
  sections: LegalSection[]
}) {
  const t = await getTranslations("legal")
  const locale = await getLocale()

  return (
    <main className="mx-auto max-w-5xl space-y-10 px-6 py-12">
      <header className="space-y-4">
        <h1 className="font-heading text-4xl font-medium tracking-tight">
          {title}
        </h1>
        <p className="text-sm text-muted-foreground">
          {locale !== DEFAULT_LOCALE && (
            <span className="block pb-2">{t("englishOnly")}</span>
          )}
          {t("updated")} <time dateTime={LEGAL_UPDATED}>{LEGAL_UPDATED}</time>
        </p>
      </header>
      {/* The documents are English only, so they read left to right in every interface. */}
      <div lang="en" dir="ltr" className="space-y-10">
        <p className="text-base leading-relaxed text-muted-foreground">
          {intro}
        </p>
        {sections.map((section) => (
          <section key={section.heading} className="space-y-3">
            <h2 className="font-heading text-2xl font-medium">
              {section.heading}
            </h2>
            {section.paragraphs?.map((paragraph) => (
              <p
                key={paragraph}
                className="text-base leading-relaxed text-muted-foreground"
              >
                {paragraph}
              </p>
            ))}
            {section.items && (
              <ul className="list-disc space-y-2 ps-5 text-base leading-relaxed text-muted-foreground">
                {section.items.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            )}
          </section>
        ))}
      </div>
    </main>
  )
}
