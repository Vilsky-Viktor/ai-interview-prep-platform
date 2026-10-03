import { ClipboardPasteIcon, ListChecksIcon, TargetIcon } from "lucide-react"
import { getTranslations } from "next-intl/server"

const STEPS = [
  { key: "paste", icon: ClipboardPasteIcon },
  { key: "review", icon: ListChecksIcon },
  { key: "practice", icon: TargetIcon },
] as const

export async function HowItWorks() {
  const t = await getTranslations("landing.how")

  return (
    <section id="how" className="scroll-mt-20 space-y-10">
      <h2 className="font-heading text-3xl font-medium tracking-tight">
        {t("title")}
      </h2>
      <ol className="grid gap-6 md:grid-cols-3">
        {STEPS.map(({ key, icon: Icon }, index) => (
          <li
            key={key}
            className="space-y-3 rounded-3xl bg-card p-6 shadow-sm ring-1 ring-foreground/5"
          >
            <div className="flex items-center gap-3">
              <span className="flex size-10 items-center justify-center rounded-full bg-primary/10 text-primary">
                <Icon className="size-5" />
              </span>
              <span className="text-sm text-muted-foreground tabular-nums">
                {index + 1}
              </span>
            </div>
            <h3 className="font-heading text-lg font-medium">
              {t(`${key}.title`)}
            </h3>
            <p className="text-sm leading-relaxed text-muted-foreground">
              {t(`${key}.text`)}
            </p>
          </li>
        ))}
      </ol>
    </section>
  )
}
