import { ArrowUpIcon, CheckIcon } from "lucide-react"
import { getTranslations } from "next-intl/server"

import { LandingSection, PANEL, Stage } from "@/components/landing/section"

const TOPICS = [
  { key: "design", checked: true },
  { key: "sql", checked: true },
  { key: "behavior", checked: true },
  { key: "basics", checked: false },
] as const

export async function ControlSection() {
  const t = await getTranslations("landing.control")

  return (
    <LandingSection title={t("title")} text={t("text")}>
      <Stage>
        <div className="space-y-3">
          <ul className={`${PANEL} divide-y divide-border/70`}>
            {TOPICS.map(({ key, checked }) => (
              <li key={key} className="flex items-center gap-3 px-5 py-4">
                {checked ? (
                  <span className="flex size-4 items-center justify-center rounded-[5px] bg-primary text-primary-foreground">
                    <CheckIcon className="size-3" />
                  </span>
                ) : (
                  <span className="size-4 rounded-[5px] border border-input" />
                )}
                <span
                  className={checked ? "" : "text-muted-foreground line-through"}
                >
                  {t(`topics.${key}`)}
                </span>
              </li>
            ))}
          </ul>
          <div
            className={`${PANEL} flex items-center justify-between gap-3 rounded-full py-2 ps-5 pe-2 text-muted-foreground`}
          >
            <span>{t("change")}</span>
            <span className="flex size-8 shrink-0 items-center justify-center rounded-full bg-primary text-primary-foreground">
              <ArrowUpIcon className="size-4" />
            </span>
          </div>
        </div>
      </Stage>
    </LandingSection>
  )
}
