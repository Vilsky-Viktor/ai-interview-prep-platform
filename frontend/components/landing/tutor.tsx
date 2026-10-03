import { CheckIcon, XIcon } from "lucide-react"
import { getTranslations } from "next-intl/server"

import { LandingSection, Mockup } from "@/components/landing/section"

// The picture's answer: the first option chosen, the second one right.
const OPTIONS = [
  {
    key: "first",
    style: "border-red-600 text-red-600 dark:border-red-400 dark:text-red-400",
    icon: XIcon,
  },
  {
    key: "second",
    style:
      "border-green-600 text-green-600 dark:border-green-400 dark:text-green-400",
    icon: CheckIcon,
  },
  { key: "third", style: "border-transparent bg-muted/60", icon: null },
] as const

export async function TutorSection() {
  const t = await getTranslations("landing.tutor")

  return (
    <LandingSection title={t("title")} text={t("text")}>
      <Mockup>
        <p className="font-medium">{t("question")}</p>
        <ul className="space-y-2">
          {OPTIONS.map(({ key, style, icon: Icon }) => (
            <li
              key={key}
              className={`flex items-center justify-between gap-3 rounded-2xl border px-4 py-3 text-sm ${style}`}
            >
              <span>{t(`options.${key}`)}</span>
              {Icon && <Icon className="size-4 shrink-0" />}
            </li>
          ))}
        </ul>
        <div className="space-y-2 pt-2 text-sm">
          <p className="ms-auto w-fit max-w-[85%] rounded-2xl bg-primary px-4 py-2 text-primary-foreground">
            {t("ask")}
          </p>
          <p className="w-fit max-w-[85%] rounded-2xl bg-muted px-4 py-2">
            {t("answer")}
          </p>
        </div>
      </Mockup>
    </LandingSection>
  )
}
