import { getTranslations } from "next-intl/server"

import { AnswerOptions } from "@/components/questions/answer-options"
import { QuestionText } from "@/components/questions/question-text"
import type { SampleQuestion } from "@/types/superadmin"

/** A role's sample interview questions with their answers: questions already public in free
 * practice, never ones candidates still get. In the template's language. */
export async function SampleQuestions({
  questions,
  language,
}: {
  questions: SampleQuestion[]
  language: string
}) {
  const t = await getTranslations("tests")

  return (
    <section className="space-y-4">
      <h2 className="font-heading text-2xl font-medium">{t("questions")}</h2>
      <p className="text-base text-muted-foreground">{t("questionsText")}</p>
      <ol lang={language} className="divide-y rounded-2xl border">
        {questions.map((question) => (
          <li key={question.id} className="space-y-3 p-6">
            <p className="text-sm text-muted-foreground">{question.topic}</p>
            <QuestionText text={question.text} className="text-base" />
            <AnswerOptions options={question.options} />
          </li>
        ))}
      </ol>
    </section>
  )
}
