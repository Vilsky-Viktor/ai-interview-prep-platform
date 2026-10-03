import { AwardIcon, CheckIcon } from "lucide-react"
import { getTranslations } from "next-intl/server"

import { LandingSection, Mockup } from "@/components/landing/section"
import { serverFetch } from "@/lib/server-api"

// The picture's progress, on the same sample topics as the plan above.
const TOPICS = [
  { key: "design", progress: 100 },
  { key: "sql", progress: 64 },
  { key: "behavior", progress: 30 },
] as const

export async function ProofSection() {
  const t = await getTranslations("landing.proof")
  const topics = await getTranslations("landing.control.topics")
  // The rules come from the rounds service, which decides them.
  const rules = await serverFetch<string[]>("/rounds/certificates/rules")

  const extra = rules?.length ? (
    <div className="space-y-2 pt-2">
      <h3 className="text-sm font-medium">{t("rules")}</h3>
      <ul className="space-y-2 text-sm text-muted-foreground">
        {rules.map((rule) => (
          <li key={rule} className="flex gap-2">
            <CheckIcon className="mt-0.5 size-4 shrink-0 text-primary" />
            <span>{rule}</span>
          </li>
        ))}
      </ul>
    </div>
  ) : null

  return (
    <LandingSection title={t("title")} text={t("text")} extra={extra} reverse>
      <Mockup className="space-y-5">
        {TOPICS.map(({ key, progress }) => (
          <div key={key} className="space-y-2">
            <div className="flex items-center justify-between gap-3 text-sm">
              <span>{topics(key)}</span>
              {progress === 100 && (
                <span className="flex items-center gap-1 rounded-full bg-primary/10 px-2.5 py-1 text-xs font-medium text-primary">
                  <AwardIcon className="size-3.5" />
                  {t("certificate")}
                </span>
              )}
            </div>
            <div className="h-2 overflow-hidden rounded-full bg-muted">
              <div
                className="h-full rounded-full bg-primary"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>
        ))}
      </Mockup>
    </LandingSection>
  )
}
