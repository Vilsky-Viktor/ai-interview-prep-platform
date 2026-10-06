"use client"

import { useTranslations } from "next-intl"
import { useEffect, useState } from "react"
import { toast } from "sonner"

import { QuestionRow } from "@/components/questions/question-row"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { VirtualList } from "@/components/virtual-list"
import { ApiError, apiFetch } from "@/lib/api"
import type { QuestionStats } from "@/types/feedback"

export function TopicQuestions({
  title,
  path,
  regeneratePath,
  wrongPath,
  reportsPath,
}: {
  title: string
  path: string
  regeneratePath?: string
  wrongPath?: string
  reportsPath?: string
}) {
  const t = useTranslations("questions")
  const common = useTranslations("common")
  const [open, setOpen] = useState(false)
  const [questions, setQuestions] = useState<QuestionStats[] | null>(null)
  const [missing, setMissing] = useState(false)
  const [regeneratingId, setRegeneratingId] = useState<string | null>(null)

  useEffect(() => {
    if (!open || questions) {
      return
    }

    let cancelled = false

    apiFetch<QuestionStats[]>(path)
      .then((rows) => {
        if (!cancelled) {
          setQuestions(rows)
        }
      })
      .catch(() => {
        if (!cancelled) {
          setMissing(true)
        }
      })

    return () => {
      cancelled = true
    }
  }, [open, questions, path])

  async function regenerate(questionId: string) {
    setRegeneratingId(questionId)

    try {
      const fresh = await apiFetch<{ id: string; text: string }>(
        `${regeneratePath}/${questionId}/regenerate`,
        { method: "POST" }
      )
      setQuestions((rows) =>
        (rows ?? []).map((row) =>
          row.id === questionId
            ? { ...row, text: fresh.text, likes: 0, dislikes: 0, reports: 0 }
            : row
        )
      )
      toast.success(t("regenerated"))
    } catch (error) {
      toast.error(
        error instanceof ApiError && error.status === 429
          ? error.message
          : t("regenerateFailed")
      )
    } finally {
      setRegeneratingId(null)
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger
        render={<Button variant="outline" className="h-9 shrink-0 px-4" />}
      >
        {t("manage")}
      </DialogTrigger>
      <DialogContent
        showCloseButton={false}
        className={regeneratePath ? "sm:max-w-4xl" : "sm:max-w-3xl"}
      >
        <DialogHeader>
          <DialogTitle className="normal-case">{title}</DialogTitle>
        </DialogHeader>
        {questions ? (
          <VirtualList
            items={questions}
            getKey={(question) => question.id}
            // A question with its four answer options.
            estimateSize={200}
            scrollClassName="max-h-[60vh] [scrollbar-width:thin] [scrollbar-color:var(--color-border)_transparent] overflow-y-auto rounded-xl border"
            className="divide-y"
            renderItem={(question, index) => (
              <QuestionRow
                question={question}
                number={index + 1}
                canRegenerate={Boolean(regeneratePath)}
                wrongPath={wrongPath}
                reportsPath={reportsPath}
                regenerating={regeneratingId === question.id}
                busy={regeneratingId !== null}
                onRegenerate={() => regenerate(question.id)}
              />
            )}
          />
        ) : (
          <p className="text-muted-foreground">
            {missing ? t("loadFailed") : common("loading")}
          </p>
        )}
        <DialogFooter showCloseButton />
      </DialogContent>
    </Dialog>
  )
}
