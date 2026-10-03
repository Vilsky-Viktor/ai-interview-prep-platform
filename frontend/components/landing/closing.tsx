import Link from "next/link"
import { getTranslations } from "next-intl/server"

import { StartButton } from "@/components/landing/start-button"

/** The landing page's end: a link to the FAQ, and a way back to the input. */
export async function Closing() {
  const t = await getTranslations("landing")

  return (
    <>
      <section className="flex flex-wrap items-baseline justify-between gap-4 border-y py-8">
        <div className="space-y-1">
          <h2 className="no-dot font-heading text-xl font-medium">
            {t("faq.title")}
          </h2>
          <p className="text-muted-foreground">{t("faq.text")}</p>
        </div>
        <Link
          href="/faq"
          className="text-primary underline-offset-4 hover:underline"
        >
          {t("faq.read")} →
        </Link>
      </section>
      <section className="space-y-8 py-12 text-center">
        <h2 className="no-dot font-heading text-4xl font-medium tracking-tight sm:text-6xl">
          {t("ready.title")}
        </h2>
        <StartButton label={t("ready.start")} />
      </section>
    </>
  )
}
