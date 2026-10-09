import { notFound } from "next/navigation"
import { getTranslations } from "next-intl/server"

import { DeleteTemplate } from "@/components/superadmin/delete-template"
import { BackLink } from "@/components/back-link"
import { EditableTitle } from "@/components/editable-title"
import { PageHeader } from "@/components/page-header"
import { SubtopicList } from "@/components/questions/subtopic-list"
import { TopicQuestionLimit } from "@/components/questions/topic-question-limit"
import { TopicQuestions } from "@/components/questions/topic-questions"
import { serverFetch } from "@/lib/server-api"
import { translatedTitle } from "@/lib/site"
import type { Template } from "@/types/superadmin"
import { LIST_BOX } from "@/constants/lists"

export const generateMetadata = () => translatedTitle("superadmin", "templates")

/** One template: rename or delete it, and check or re-generate its questions. */
export default async function TemplatePage({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params
  const t = await getTranslations("superadmin")
  const template = await serverFetch<Template>(
    `/library/superadmin/templates/${id}`
  )

  if (!template) {
    notFound()
  }

  const base = `/library/superadmin/templates/${id}`

  return (
    <main className="mx-auto max-w-5xl space-y-8 px-6 py-12">
      <PageHeader
        back={
          <BackLink href="/superadmin/templates">{t("templates")}</BackLink>
        }
        title={
          <div className="flex items-start justify-between gap-4">
            <div className="min-w-0 flex-1">
              <EditableTitle title={template.title} path={`${base}/title`} />
            </div>
            <DeleteTemplate templateId={id} title={template.title} />
          </div>
        }
      />

      <ul className={LIST_BOX}>
        {template.topics.map((topic) => (
          // On phones the questions' button and count go under the subtopics, centered.
          <li
            key={topic.id}
            className="flex items-center justify-between gap-6 p-4 max-sm:flex-col max-sm:items-stretch max-sm:px-6 max-sm:py-8 sm:p-6"
          >
            <span className="max-w-3xl min-w-0 space-y-3">
              <span className="block text-lg font-medium">{topic.title}</span>
              <SubtopicList subtopics={topic.subtopics} />
            </span>
            <span className="flex shrink-0 flex-col items-center gap-3 max-sm:flex-row max-sm:flex-wrap max-sm:justify-center max-sm:gap-4">
              <TopicQuestions
                title={topic.title}
                path={`${base}/topics/${topic.id}/questions`}
                regeneratePath={`/generate/superadmin/templates/${id}/questions`}
                wrongPath={`${base}/questions`}
                reportsPath={`${base}/questions`}
              />
              <TopicQuestionLimit count={topic.question_count} limit={null} />
            </span>
          </li>
        ))}
      </ul>
    </main>
  )
}
