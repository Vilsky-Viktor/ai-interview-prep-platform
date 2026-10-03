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
      <ol className="mx-auto w-full max-w-2xl space-y-8">
        {STEPS.map((key, index) => (
          <li key={key} className="flex gap-6 border-t pt-6">
            <span className="font-heading text-2xl text-primary tabular-nums">
              {String(index + 1).padStart(2, "0")}
            </span>
            <div className="space-y-2">
              <h3 className="font-heading text-2xl font-medium">
                {t(`${key}.title`)}
              </h3>
              <p className="text-lg leading-relaxed text-muted-foreground">
                {t(`${key}.text`)}
              </p>
            </div>
          </li>
        ))}
      </ol>
    </section>
  )
}
