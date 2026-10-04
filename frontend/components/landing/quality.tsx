import { getLocale, getNow, getTranslations } from "next-intl/server"

import { QualityDemo } from "@/components/landing/quality-demo"
import { LandingSection, Stage } from "@/components/landing/section"
import { formatDate } from "@/lib/format"

/** A topic's questions as their owner sees them, playing a short demo of a weak question's
 * report opened and the question re-generated. */
export async function QualitySection() {
  const t = await getTranslations("landing.quality")
  const questions = await getTranslations("questions")
  const reasons = await getTranslations("reportReasons")
  const reported = formatDate((await getNow()).toISOString(), await getLocale())

  return (
    <LandingSection title={t("title")} text={t("text")}>
      <Stage>
        <QualityDemo
          title={t("list")}
          good={t("items.good")}
          weak={t("items.weak")}
          better={t("items.better")}
          report={{
            reason: reasons("unclear"),
            date: reported,
            comment: t("comment"),
          }}
          labels={{
            regenerate: questions("regenerate"),
            regenerating: questions("regenerating"),
          }}
        />
      </Stage>
    </LandingSection>
  )
}
