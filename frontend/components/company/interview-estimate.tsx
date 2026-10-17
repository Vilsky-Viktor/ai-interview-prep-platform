import { useTranslations } from "next-intl"

/** What the interview adds up to for each candidate, as the API counts it: every question they
 * get, the time each has, and the whole interview's time; three outlined cards in a row, each
 * with its title beside its number (stacked on phones). */
export function InterviewEstimate({
  questions,
  questionSeconds,
  minutes,
}: {
  questions: number
  questionSeconds: number
  minutes: number
}) {
  const t = useTranslations("interviews")
  const tInvite = useTranslations("invite")
  const facts = [
    { key: "total-questions", label: t("totalQuestions"), value: questions },
    {
      key: "question-seconds",
      label: tInvite("timePerQuestion"),
      value: questionSeconds,
      unit: tInvite("secondsUnit"),
    },
    {
      key: "total-minutes",
      label: tInvite("wholeInterview"),
      value: minutes,
      unit: tInvite("minutesUnit"),
    },
  ]

  return (
    <ul className="grid gap-3 sm:grid-cols-3" data-testid="interview-estimate">
      {facts.map(({ key, label, value, unit }) => (
        <li
          key={key}
          data-testid={key}
          className="flex items-center justify-between gap-4 rounded-2xl border p-5"
        >
          <span className="text-sm text-muted-foreground">{label}</span>
          <span className="shrink-0 text-base whitespace-nowrap text-muted-foreground">
            <span className="text-3xl font-medium text-foreground tabular-nums">
              {value}
            </span>
            {unit && ` ${unit}`}
          </span>
        </li>
      ))}
    </ul>
  )
}
