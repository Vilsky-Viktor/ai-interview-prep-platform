import { CheckIcon, XIcon } from "lucide-react"
import { getTranslations } from "next-intl/server"

import { LandingSection, PANEL, Stage } from "@/components/landing/section"

// The picture's answer: the first option chosen, the second one right.
const OPTIONS = [
  { key: "first", style: "border-border text-muted-foreground", icon: XIcon },
  { key: "second", style: "border-primary text-primary", icon: CheckIcon },
  { key: "third", style: "border-border/70", icon: null },
] as const

export async function TutorSection() {
  const t = await getTranslations("landing.tutor")

  return (
    <LandingSection title={t("title")} text={t("text")}>
      <Stage>
        <div className={`${PANEL} space-y-3 p-5 text-base`}>
          <p className="text-lg font-medium">{t("question")}</p>
          <ul className="space-y-2">
            {OPTIONS.map(({ key, style, icon: Icon }) => (
              <li
                key={key}
                className={`flex items-center justify-between gap-3 rounded-xl border px-5 py-2.5 ${style}`}
              >
                <span>{t(`options.${key}`)}</span>
                {Icon && <Icon className="size-4 shrink-0" />}
              </li>
            ))}
          </ul>
          <div className="space-y-2 pt-1">
            <p className="ms-auto w-fit max-w-[85%] rounded-2xl bg-primary px-4 py-2 text-primary-foreground">
              {t("ask")}
            </p>
            <p className="w-fit max-w-[90%] rounded-2xl bg-muted px-4 py-2">
              {t("answer")}
            </p>
          </div>
        </div>
      </Stage>
    </LandingSection>
  )
}
