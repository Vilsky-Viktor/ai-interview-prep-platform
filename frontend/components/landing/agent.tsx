import { BadgeQuestionMarkIcon } from "lucide-react"
import { getTranslations } from "next-intl/server"

import { AgentDemo } from "@/components/landing/agent-demo"
import { AskAgentButton } from "@/components/landing/ask-agent-button"
import { LandingSection, Stage } from "@/components/landing/section"

const POINTS = ["answers", "acts", "voice", "help"] as const
// What the preview's input types, one after another, to show what the agent can do.
const TYPED = ["best", "create", "passMark", "ats", "credits"] as const

/** The assistant: a request in its panel and the card it prepares for the user to confirm, and
 * what else it does, with the button that opens it. */
export async function AgentSection() {
  const t = await getTranslations("landing.agent")

  return (
    <LandingSection title={t("title")} text={t("text")}>
      {/* The button sits on the picture's top edge, half over its background, like "browse"
          in the try-first section. */}
      <div className="relative mt-4">
        <div className="absolute start-1/2 top-0 z-10 -translate-x-1/2 -translate-y-1/2 rtl:translate-x-1/2">
          <AskAgentButton className="h-11 bg-background" />
        </div>
        <Stage>
          <AgentDemo
            question={t("demo.question")}
            typed={TYPED.map((key) => t(`demo.typed.${key}`))}
          />
        </Stage>
      </div>
      <ul className="mx-auto grid w-full max-w-2xl gap-x-8 gap-y-3 text-muted-foreground sm:grid-cols-2">
        {POINTS.map((point) => (
          <li key={point} className="flex gap-3">
            <span className="mt-2.5 size-1.5 shrink-0 rounded-full bg-primary" />
            <span>
              {t(`points.${point}`)}
              {point === "help" && (
                <BadgeQuestionMarkIcon
                  aria-hidden
                  className="ms-1.5 inline size-4 align-[-0.15em] text-foreground"
                />
              )}
            </span>
          </li>
        ))}
      </ul>
    </LandingSection>
  )
}
