import { cn } from "cn"
import { CheckIcon, MinusIcon } from "lucide-react"
import { getTranslations } from "next-intl/server"

import { LandingSection, Stage } from "@/components/landing/section"
import { buttonVariants } from "@/components/ui/button"
import { serverFetch } from "@/lib/server-api"

// The picture's topics on a kit page (on phones the button and the bar take their own lines, as there): one with its certificate earned, one under way.
const TOPICS = [
  { key: "design", questions: 24, progress: 100, done: true },
  { key: "sql", questions: 18, progress: 64, done: false },
] as const

const OUTLINE = buttonVariants({ variant: "outline", className: "lowercase" })

/** Topics on a kit page as they really look (app/preparations/[id]/page.tsx), and what the
 * certificate button's dialog says (components/rounds/certificate-button.tsx). */
export async function ProofSection() {
  const t = await getTranslations("landing.proof")
  const control = await getTranslations("landing.control")
  const rounds = await getTranslations("rounds")
  const questions = await getTranslations("questions")
  const certificate = await getTranslations("certificate")
  const preparations = await getTranslations("preparations")
  // The rules come from the rounds service, which decides them.
  const rules = await serverFetch<string[]>("/rounds/certificates/rules")
  // The picture keeps the first rule (every question) and the last (the pass mark).
  const shown = rules?.length ? [rules[0], rules[rules.length - 1]] : []

  return (
    <LandingSection title={t("title")} text={t("text")}>
      <Stage>
        <div className="text-start">
          <ul className="divide-y rounded-2xl border bg-background">
            {TOPICS.map(({ key, questions: count, progress, done }) => (
              <li key={key} className="space-y-4 p-5">
                <div className="flex flex-col items-start gap-4 sm:flex-row sm:justify-between sm:gap-6">
                  <span className="min-w-0 space-y-1">
                    <span className="block text-xl font-medium">
                      {control(`topics.${key}`)}
                    </span>
                    <span className="block text-sm text-muted-foreground">
                      {(control.raw(`subtopics.${key}`) as string[]).map(
                        (subtopic, index) => (
                          <span key={subtopic}>
                            {index > 0 && (
                              <MinusIcon className="mx-1.5 inline size-3.5 align-[-2px] text-foreground/55" />
                            )}
                            {subtopic}
                          </span>
                        )
                      )}
                    </span>
                  </span>
                  <span
                    className={buttonVariants({
                      className: "h-10 px-6 lowercase",
                    })}
                  >
                    {done ? t("again") : rounds("continue")}
                  </span>
                </div>
                <div className="flex flex-wrap items-center justify-between gap-3 sm:grid sm:grid-cols-[auto_1fr_auto] sm:gap-5">
                  <span className="text-sm">
                    <span className="text-lg tabular-nums">{count}</span>{" "}
                    {questions("count", { count })}
                  </span>
                  <div className="order-last h-1 w-full overflow-hidden rounded-full bg-muted sm:order-none">
                    <div
                      className={cn(
                        "h-full",
                        done ? "bg-green-600 dark:bg-green-400" : "bg-primary"
                      )}
                      style={{ width: `${progress}%` }}
                    />
                  </div>
                  <span className="flex gap-2">
                    {done && (
                      <span className={OUTLINE}>{certificate("title")}</span>
                    )}
                    <span className={OUTLINE}>{preparations("history")}</span>
                  </span>
                </div>
              </li>
            ))}
          </ul>
          {shown.length ? (
            // What the certificate dialog says, a rule per card under the list.
            <ul className="mt-7 grid gap-7 sm:grid-cols-[auto_auto] sm:gap-5">
              {shown.map((rule) => (
                <li
                  key={rule}
                  className="relative rounded-2xl border bg-background px-5 pt-6 pb-5 text-[15px]"
                >
                  {/* The tick sits on the card's corner, leaving the text the whole width. */}
                  <CheckIcon className="absolute -start-4 -top-[15px] size-12 stroke-[2.5] text-primary" />
                  {rule}
                </li>
              ))}
            </ul>
          ) : null}
        </div>
      </Stage>
    </LandingSection>
  )
}
