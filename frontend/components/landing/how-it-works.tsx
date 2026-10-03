import { getTranslations } from "next-intl/server"

const STEPS = ["paste", "review", "practice"] as const

export async function HowItWorks() {
  const t = await getTranslations("landing.how")

  return (
    <section id="how" className="scroll-mt-20 space-y-12">
      <h2 className="font-heading text-3xl font-medium tracking-tight sm:text-4xl">
        {t("title")}
      </h2>
      <ol className="grid gap-10 md:grid-cols-3 md:gap-8">
        {STEPS.map((key, index) => (
          <li key={key} className="space-y-3 border-t pt-6">
            <span className="font-heading text-sm text-primary tabular-nums">
              {String(index + 1).padStart(2, "0")}
            </span>
            <h3 className="font-heading text-xl font-medium">
              {t(`${key}.title`)}
            </h3>
            <p className="leading-relaxed text-muted-foreground">
              {t(`${key}.text`)}
            </p>
          </li>
        ))}
      </ol>
    </section>
  )
}
