import { getTranslations } from "next-intl/server"

import { LandingSection, Mockup } from "@/components/landing/section"

// The order a round asks in: new questions first, then the missed ones.
const QUESTIONS = [
  { key: "first", status: "fresh", style: "bg-primary/10 text-primary" },
  {
    key: "second",
    status: "missed",
    style: "bg-red-600/10 text-red-600 dark:text-red-400",
  },
  {
    key: "third",
    status: "right",
    style: "bg-green-600/10 text-green-600 dark:text-green-400",
  },
] as const

export async function GapsSection() {
  const t = await getTranslations("landing.gaps")

  return (
    <LandingSection title={t("title")} text={t("text")} reverse>
      <Mockup>
        <ol className="space-y-3">
          {QUESTIONS.map(({ key, status, style }, index) => (
            <li
              key={key}
              className="flex items-center gap-3 rounded-2xl bg-muted/60 p-4"
            >
              <span className="text-sm text-muted-foreground tabular-nums">
                {index + 1}
              </span>
              <span className="min-w-0 flex-1 text-sm">
                {t(`questions.${key}`)}
              </span>
              <span
                className={`shrink-0 rounded-full px-2.5 py-1 text-xs font-medium ${style}`}
              >
                {t(status)}
              </span>
            </li>
          ))}
        </ol>
      </Mockup>
    </LandingSection>
  )
}
