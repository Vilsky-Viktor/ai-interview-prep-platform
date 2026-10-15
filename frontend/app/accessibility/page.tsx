import { getLocale, getTranslations } from "next-intl/server"

import {
  ACCESSIBILITY_DONE,
  ACCESSIBILITY_LIMITS,
  ACCESSIBILITY_REVIEWED,
} from "@/constants/accessibility"
import { OPERATOR } from "@/constants/operator"
import { formatDate } from "@/lib/format"
import { pageMetadata } from "@/lib/site"

export async function generateMetadata() {
  const t = await getTranslations("accessibility")

  return pageMetadata(t("title"), t("description"), "/accessibility", true)
}

/** The accessibility statement: what prepza does for people with disabilities, what falls
 * short, and how to tell us. */
export default async function AccessibilityPage() {
  const t = await getTranslations("accessibility")
  const locale = await getLocale()

  return (
    <main className="mx-auto max-w-5xl space-y-12 px-6 py-12">
      <header className="space-y-4">
        <h1 className="font-heading text-4xl font-medium tracking-tight">
          {t("title")}
        </h1>
        <p className="text-lg text-muted-foreground">{t("intro")}</p>
      </header>
      <Section
        title={t("done.title")}
        items={ACCESSIBILITY_DONE.map((key) => t(`done.${key}`))}
      />
      <Section
        title={t("limits.title")}
        items={ACCESSIBILITY_LIMITS.map((key) => t(`limits.${key}`))}
      />
      <section className="space-y-4">
        <h2 className="font-heading text-2xl font-medium tracking-tight">
          {t("feedback.title")}
        </h2>
        <p className="text-base leading-relaxed text-muted-foreground">
          {t.rich("feedback.text", {
            email: () => (
              <a
                href={`mailto:${OPERATOR.email}`}
                className="text-foreground underline"
              >
                {OPERATOR.email}
              </a>
            ),
          })}
        </p>
        <p className="text-base leading-relaxed text-muted-foreground">
          {t("feedback.authority")}
        </p>
      </section>
      <p className="text-sm text-muted-foreground">
        {t("reviewed", { date: formatDate(ACCESSIBILITY_REVIEWED, locale) })}
      </p>
    </main>
  )
}

function Section({ title, items }: { title: string; items: string[] }) {
  return (
    <section className="space-y-4">
      <h2 className="font-heading text-2xl font-medium tracking-tight">
        {title}
      </h2>
      <ul className="list-disc space-y-2 ps-6 text-base leading-relaxed text-muted-foreground">
        {items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </section>
  )
}
