import Link from "next/link"
import { getTranslations } from "next-intl/server"

import { StartButton } from "@/components/landing/start-button"
import { Button } from "@/components/ui/button"

/** The landing page's end: a link to the FAQ, and a way back to the input. */
export async function Closing() {
  const t = await getTranslations("landing")

  return (
    <>
      <section className="flex flex-wrap items-center justify-between gap-6 rounded-3xl bg-card p-8 shadow-sm ring-1 ring-foreground/5">
        <div className="space-y-2">
          <h2 className="no-dot font-heading text-2xl font-medium tracking-tight">
            {t("faq.title")}
          </h2>
          <p className="text-base text-muted-foreground">{t("faq.text")}</p>
        </div>
        <Button
          variant="outline"
          className="h-10 px-5 text-base"
          render={<Link href="/faq" />}
          nativeButton={false}
        >
          {t("faq.read")}
        </Button>
      </section>
      <section className="space-y-6 text-center">
        <h2 className="no-dot font-heading text-3xl font-medium tracking-tight sm:text-4xl">
          {t("ready.title")}
        </h2>
        <StartButton label={t("ready.start")} />
      </section>
    </>
  )
}
