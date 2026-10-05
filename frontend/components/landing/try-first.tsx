import { cn } from "cn"
import { MinusIcon, TimerIcon } from "lucide-react"
import { getTranslations } from "next-intl/server"

import {
  LandingSection,
  MoreLink,
  PANEL,
  Stage,
} from "@/components/landing/section"
import { Progress } from "@/components/ui/progress"

const POINTS = ["practice", "preview"] as const
const OPTIONS = ["a", "b", "c", "d"] as const
// The option the picture shows picked.
const PICKED = 1

/** A question as a candidate takes it (components/company/session-play.tsx): try a practice
 * test or your own interview before inviting anyone. */
export async function TryFirstSection() {
  const t = await getTranslations("landing.try")

  return (
    <LandingSection
      title={t("title")}
      text={t("text")}
      extra={
        <div className="pt-2">
          <MoreLink href="/practice">{t("browse")}</MoreLink>
        </div>
      }
    >
      <Stage>
        <div
          className={`${PANEL} space-y-6 px-6 py-5 text-start sm:px-14 sm:py-8`}
        >
          <div className="space-y-3">
            <div className="flex items-center justify-between gap-4 text-sm text-muted-foreground">
              <span className="truncate">{t("topic")}</span>
              <span className="flex shrink-0 items-center tabular-nums">
                <span className="flex items-center gap-1.5 font-medium">
                  <TimerIcon className="size-4" />
                  0:42
                </span>
                <MinusIcon className="mx-1.5 size-3.5 text-foreground/55" />3 /
                10
              </span>
            </div>
            <Progress value={30} />
          </div>
          <p className="text-xl leading-snug font-medium sm:text-2xl">
            {t("question")}
          </p>
          <ul className="space-y-2">
            {OPTIONS.map((option, index) => (
              <li
                key={option}
                className={cn(
                  "flex items-start gap-3 rounded-2xl border p-4 text-lg leading-7 font-light",
                  index === PICKED && "border-ring bg-muted"
                )}
              >
                <span className="w-4 shrink-0 text-muted-foreground">
                  {String.fromCharCode(65 + index)}
                </span>
                <span>{t(`options.${option}`)}</span>
              </li>
            ))}
          </ul>
        </div>
      </Stage>
      <ul className="mx-auto grid w-full max-w-2xl gap-x-8 gap-y-3 text-muted-foreground sm:grid-cols-2">
        {POINTS.map((point) => (
          <li key={point} className="flex gap-3">
            <span className="mt-2.5 size-1.5 shrink-0 rounded-full bg-primary" />
            <span>{t(`points.${point}`)}</span>
          </li>
        ))}
      </ul>
    </LandingSection>
  )
}
