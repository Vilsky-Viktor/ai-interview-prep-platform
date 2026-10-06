import { getTranslations } from "next-intl/server"

import { ReviewDemo } from "@/components/landing/review-demo"
import { LandingSection, Stage } from "@/components/landing/section"

// The picture's topics: the last one unchecked, as if the role doesn't need it; the first
// one is edited by hand in the demo.
const TOPICS = [
  { key: "design", checked: true },
  { key: "basics", checked: false },
] as const
const EDITED = "design"

/** The topic review, with its own labels, playing a short demo of editing it. */
export async function ControlSection() {
  const t = await getTranslations("landing.control")
  const review = await getTranslations("generation")

  return (
    <LandingSection title={t("title")} text={t("text")}>
      <Stage>
        <ReviewDemo
          title={review("reviewTitle")}
          topics={TOPICS.map(({ key, checked }) => ({
            key,
            checked,
            name: t(`topics.${key}`),
            subtopics: t.raw(`subtopics.${key}`) as string[],
          }))}
          editing={EDITED}
          added={t("added")}
          change={t("change")}
          newTopic={{
            name: t("newTopic"),
            subtopics: t.raw("newSubtopics") as string[],
          }}
          labels={{
            addSubtopic: review("addSubtopic"),
            add: review("add"),
            done: review("done"),
            placeholder: t("placeholder"),
            apply: review("apply"),
          }}
        />
      </Stage>
    </LandingSection>
  )
}
