import { QuestionRating } from "@/components/questions/question-rating"
import { ReportDialog } from "@/components/questions/report-dialog"

export function QuestionActions({
  questionId,
  basePath = `/library/questions/${questionId}`,
}: {
  questionId: string
  basePath?: string
}) {
  return (
    <div className="mx-auto grid h-14 w-60 grid-cols-3 overflow-hidden rounded-xl bg-muted">
      <QuestionRating basePath={basePath} />
      <ReportDialog basePath={basePath} />
    </div>
  )
}
