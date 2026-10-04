import { getTranslations } from "next-intl/server"

const STEPS = ["paste", "review", "practice"] as const

export async function HowItWorks() {
  const t = await getTranslations("landing.how")

  return (
    <section
      id="how"
      className="flex min-h-[calc(100svh-3.5rem)] scroll-mt-14 flex-col justify-center gap-10 py-12"
    >
      <h2 className="text-center font-heading text-4xl font-medium tracking-tight sm:text-5xl">
        {t("title")}
      </h2>
      <ol className="mx-auto w-full max-w-3xl space-y-8">
        {STEPS.map((key, index) => (
          <li key={key} className="flex gap-4 border-t pt-6 sm:gap-6">
            <span className="w-14 shrink-0 font-heading text-4xl leading-none font-medium text-primary tabular-nums sm:w-20 sm:text-5xl">
              {String(index + 1).padStart(2, "0")}
            </span>
            <div className="space-y-2">
              <h3 className="font-heading text-2xl font-medium">
                {t(`${key}.title`)}
              </h3>
              <p className="text-lg leading-relaxed whitespace-pre-line text-muted-foreground">
                {t(`${key}.text`)}
              </p>
            </div>
          </li>
        ))}
      </ol>
    </section>
  )
}
