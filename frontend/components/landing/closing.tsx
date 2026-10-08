import { getTranslations } from "next-intl/server"

import { DemosButton } from "@/components/landing/demos-button"
import { MoreLink } from "@/components/landing/section"
import { StartButton } from "@/components/landing/start-button"

/** The landing page's last screen: back to the job description box, and a link to the FAQ. */
export async function Closing() {
  const t = await getTranslations("landing")

  return (
    <section className="flex min-h-[calc(100svh-3.5rem)] flex-col items-center justify-center gap-24 py-24 text-center">
      <div className="space-y-10">
        <h2 className="no-dot font-heading text-5xl font-medium tracking-tight sm:text-7xl">
          {t("ready.title")}
        </h2>
        <div className="flex flex-wrap justify-center gap-3">
          <StartButton label={t("ready.start")} />
          <DemosButton />
        </div>
      </div>
      <div className="space-y-3">
        <h3 className="font-heading text-2xl font-medium">{t("faq.title")}</h3>
        <p className="text-lg text-muted-foreground">{t("faq.text")}</p>
        <MoreLink href="/faq" keepCase>
          {t("faq.read")}
        </MoreLink>
      </div>
    </section>
  )
}
