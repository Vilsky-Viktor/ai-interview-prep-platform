import { getTranslations } from "next-intl/server"

import { LandingSection, PANEL, Stage } from "@/components/landing/section"
import { serverFetch } from "@/lib/server-api"

// The picture's progress, on the same sample topics as the plan above.
const TOPICS = [
  { key: "design", progress: 100 },
  { key: "sql", progress: 64 },
] as const

export async function ProofSection() {
  const t = await getTranslations("landing.proof")
  const topics = await getTranslations("landing.control.topics")
  // The rules come from the rounds service, which decides them.
  const rules = await serverFetch<string[]>("/rounds/certificates/rules")

  return (
    <LandingSection title={t("title")} text={t("text")}>
      <Stage>
        <div className="space-y-4">
          <ul className={`${PANEL} divide-y divide-border/70 text-base`}>
            {TOPICS.map(({ key, progress }) => (
              <li key={key} className="space-y-2.5 px-6 py-4">
                <div className="flex items-center justify-between gap-3">
                  <span>{topics(key)}</span>
                  {progress === 100 ? (
                    <span className="text-sm font-medium text-primary">
                      {t("certificate")}
                    </span>
                  ) : (
                    <span className="text-sm text-muted-foreground tabular-nums">
                      {progress}%
                    </span>
                  )}
                </div>
                <div className="h-1.5 overflow-hidden rounded-full bg-muted">
                  <div
                    className="h-full rounded-full bg-primary"
                    style={{ width: `${progress}%` }}
                  />
                </div>
              </li>
            ))}
          </ul>
          {rules?.length ? (
            <div className={`${PANEL} space-y-3 px-6 py-5 text-base`}>
              <p className="font-medium">{t("rules")}</p>
              <ol className="space-y-1.5 text-muted-foreground">
                {rules.map((rule, index) => (
                  <li key={rule} className="flex gap-3">
                    <span className="text-primary tabular-nums">
                      {index + 1}
                    </span>
                    <span>{rule}</span>
                  </li>
                ))}
              </ol>
            </div>
          ) : null}
        </div>
      </Stage>
    </LandingSection>
  )
}
