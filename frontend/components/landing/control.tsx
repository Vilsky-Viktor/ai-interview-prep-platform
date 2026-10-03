import { CheckIcon, SendIcon } from "lucide-react"
import { getTranslations } from "next-intl/server"

import { LandingSection, Mockup } from "@/components/landing/section"

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
      <Mockup>
        <ul className="divide-y">
          {TOPICS.map(({ key, checked }) => (
            <li key={key} className="flex items-center gap-3 py-3">
              <span
                className={
                  checked
                    ? "flex size-4 items-center justify-center rounded-[6px] bg-primary text-primary-foreground"
                    : "size-4 rounded-[6px] border border-input"
                }
              >
                {checked && <CheckIcon className="size-3.5" />}
              </span>
              <span
                className={checked ? "" : "text-muted-foreground line-through"}
              >
                {t(`topics.${key}`)}
              </span>
            </li>
          ))}
        </ul>
        <div className="flex items-center justify-between gap-3 rounded-full bg-muted px-4 py-2 text-sm text-muted-foreground">
          <span>{t("change")}</span>
          <SendIcon className="size-4 rtl:-scale-x-100" />
        </div>
      </Mockup>
    </LandingSection>
  )
}
