import { getTranslations } from "next-intl/server"

import { LandingSection, PANEL, Stage } from "@/components/landing/section"
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
    <div className="space-y-3 pt-4">
      <h3 className="text-sm font-medium">{t("rules")}</h3>
      <ol className="space-y-2 text-muted-foreground">
        {rules.map((rule, index) => (
          <li key={rule} className="flex gap-3">
            <span className="text-primary tabular-nums">{index + 1}</span>
            <span>{rule}</span>
          </li>
        ))}
      </ol>
    </div>
  ) : null

  return (
    <LandingSection title={t("title")} text={t("text")} extra={extra}>
      <Stage>
        <ul className={`${PANEL} divide-y divide-border/70`}>
          {TOPICS.map(({ key, progress }) => (
            <li key={key} className="space-y-3 px-5 py-4">
              <div className="flex items-center justify-between gap-3">
                <span>{topics(key)}</span>
                {progress === 100 ? (
                  <span className="text-xs font-medium text-primary">
                    {t("certificate")}
                  </span>
                ) : (
                  <span className="text-xs text-muted-foreground tabular-nums">
                    {progress}%
                  </span>
                )}
              </div>
              <div className="h-1 overflow-hidden rounded-full bg-muted">
                <div
                  className="h-full rounded-full bg-primary"
                  style={{ width: `${progress}%` }}
                />
              </div>
            </li>
          ))}
        </ul>
      </Stage>
    </LandingSection>
  )
}
