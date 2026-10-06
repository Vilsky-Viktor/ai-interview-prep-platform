import { getLocale, getNow, getTranslations } from "next-intl/server"

import {
  type DemoQuestion,
  QualityDemo,
} from "@/components/landing/quality-demo"
import { LandingSection, Stage } from "@/components/landing/section"
import { formatDate } from "@/lib/format"

// Which option of each pictured question is right; the weak one's key is debatable on purpose.
const CORRECT = { good: 0, weak: 2, better: 1 } as const

/** A topic's questions as their owner sees them, playing a short demo of a weak question's
 * report opened and the question re-generated. */
export async function QualitySection() {
  const t = await getTranslations("landing.quality")
  const questions = await getTranslations("questions")
  const reasons = await getTranslations("reportReasons")
  // A question of the picture with its options, the right one at CORRECT's place.
  const question = (key: keyof typeof CORRECT): DemoQuestion => ({
    text: t(`items.${key}`),
    options: (t.raw(`options.${key}`) as string[]).map((answer, index) => ({
      answer,
      correct: index === CORRECT[key],
    })),
  })
  const reported = formatDate((await getNow()).toISOString(), await getLocale())

  return (
    <LandingSection title={t("title")} text={t("text")}>
      <Stage>
        <QualityDemo
          title={t("list")}
          good={question("good")}
          weak={question("weak")}
          better={question("better")}
          report={{
            reason: reasons("unclear"),
            date: reported,
            comment: t("comment"),
          }}
          labels={{
            regenerate: questions("regenerate"),
            regenerating: questions("regenerating"),
            wrongAnswer: questions("wrongAnswer"),
          }}
        />
      </Stage>
    </LandingSection>
  )
}
