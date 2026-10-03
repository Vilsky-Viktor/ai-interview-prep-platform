"use client"

import { cn } from "cn"
import { useTranslations } from "next-intl"
import { useEffect, useState } from "react"
import { toast } from "sonner"

import { QuestionRow } from "@/components/questions/question-row"
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
  count,
  path,
  regeneratePath,
  reportsPath,
  alignCount = false,
}: {
  title: string
  count: number
  path: string
  regeneratePath?: string
  reportsPath?: string
  // Reserve room for three digits, so rows with 99 and 100 questions line up.
  alignCount?: boolean
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
        render={
          <button
            type="button"
            className="shrink-0 cursor-pointer text-sm text-foreground transition-colors hover:text-primary"
          />
        }
      >
        <span
          className={cn(
            "text-lg tabular-nums",
            alignCount && "inline-block min-w-[3ch] text-right"
          )}
        >
          {count}
        </span>{" "}
        {t("count", { count })}
      </DialogTrigger>
      <DialogContent
        showCloseButton={false}
        className={regeneratePath ? "sm:max-w-4xl" : "sm:max-w-3xl"}
      >
        <DialogHeader>
          <DialogTitle>{title}</DialogTitle>
        </DialogHeader>
        {questions ? (
          <VirtualList
            items={questions}
            getKey={(question) => question.id}
            estimateSize={88}
            scrollClassName="max-h-[60vh] [scrollbar-width:thin] [scrollbar-color:var(--color-border)_transparent] overflow-y-auto rounded-xl border"
            className="divide-y"
            renderItem={(question, index) => (
              <QuestionRow
                question={question}
                number={index + 1}
                canRegenerate={Boolean(regeneratePath)}
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
