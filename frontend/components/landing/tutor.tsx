import { cn } from "cn"
import { getTranslations } from "next-intl/server"

import { LandingSection, Stage } from "@/components/landing/section"
import { TutorChatDemo } from "@/components/landing/tutor-chat-demo"

const OPTIONS = ["first", "second", "third", "fourth"] as const
// The picture's answer: the first option picked, the second one correct.
const PICKED = 0
const CORRECT = 1
/** An answered question in a round as it really looks (components/rounds/round-view.tsx): the
 * options with the right one shown, then a follow-up question to the tutor, played as a demo. */
export async function TutorSection() {
  const t = await getTranslations("landing.tutor")
  const rounds = await getTranslations("rounds")
  const common = await getTranslations("common")

  function optionClass(index: number) {
    if (index === CORRECT) {
      return "border-green-600 bg-green-600/15 dark:border-green-400 dark:bg-green-400/15"
    }

    return index === PICKED
      ? "border-destructive bg-destructive/10"
      : "opacity-60"
  }

  return (
    <LandingSection title={t("title")} text={t("text")}>
      <Stage>
        <div className="space-y-4 rounded-2xl border bg-background px-9 py-6 text-start">
          {/* The round's progress, as the real header shows it: 4 of 12 answered. */}
          <div className="h-1 overflow-hidden rounded-full bg-muted">
            <div className="h-full w-1/3 bg-primary" />
          </div>
          <p className="text-lg leading-snug font-medium">{t("question")}</p>
          <ul className="space-y-2">
            {OPTIONS.map((key, index) => (
              <li
                key={key}
                className={cn(
                  "flex items-start gap-3 rounded-2xl border px-4 py-2.5 font-light",
                  optionClass(index)
                )}
              >
                <span className="w-4 shrink-0 text-muted-foreground">
                  {String.fromCharCode(65 + index)}
                </span>
                <span>{t(`options.${key}`)}</span>
              </li>
            ))}
          </ul>
          <TutorChatDemo
            ask={t("ask")}
            answer={t("answer")}
            placeholder={rounds("followUpPlaceholder")}
            thinking={common("thinking")}
          />
        </div>
      </Stage>
    </LandingSection>
  )
}
