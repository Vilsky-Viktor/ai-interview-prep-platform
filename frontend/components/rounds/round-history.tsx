"use client"

import { cn } from "cn"
import { Trash2Icon } from "lucide-react"
import Link from "next/link"
import { useLocale, useTranslations } from "next-intl"
import { useState, type ReactNode } from "react"
import { toast } from "sonner"

import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { VirtualList } from "@/components/virtual-list"
import { usePagedList } from "@/hooks/use-paged-list"
import { apiFetch } from "@/lib/api"
import { formatDate } from "@/lib/format"
import { clearRoundCursor } from "@/lib/round-cursor"
import type { Round } from "@/types/round"

type Pending = { id: string; kind: "delete" | "finish" }

export function RoundHistory({
  topicId,
  rounds,
  back,
  title,
}: {
  topicId: string
  // The first page, already rendered by the server; the rest load as the user scrolls.
  rounds: Round[]
  back: ReactNode
  title: ReactNode
}) {
  const t = useTranslations("rounds")
  const common = useTranslations("common")
  const locale = useLocale()
  const { items, setItems, loadMore } = usePagedList(
    `/rounds/topics/${topicId}/rounds`,
    rounds
  )
  const [selected, setSelected] = useState<string[]>([])
  const [pending, setPending] = useState<Pending | null>(null)
  const [busy, setBusy] = useState(false)
  const pendingRound = items.find((item) => item.id === pending?.id)

  function toggle(id: string, checked: boolean) {
    setSelected((current) =>
      checked
        ? [...current, id].slice(-2)
        : current.filter((item) => item !== id)
    )
  }

  async function confirm() {
    if (!pending) {
      return
    }

    setBusy(true)

    try {
      if (pending.kind === "delete") {
        await apiFetch(`/rounds/rounds/${pending.id}`, { method: "DELETE" })
        setItems((current) => current.filter((item) => item.id !== pending.id))
        setSelected((current) => current.filter((item) => item !== pending.id))
      } else {
        clearRoundCursor(pending.id)
        const finished = await apiFetch<Round>(
          `/rounds/rounds/${pending.id}/finish`,
          { method: "POST" }
        )
        setItems((current) =>
          current.map((item) => (item.id === finished.id ? finished : item))
        )
      }

      setPending(null)
    } catch {
      toast.error(
        pending.kind === "delete" ? t("deleteFailed") : t("finishFailed")
      )
    } finally {
      setBusy(false)
    }
  }

  const finishing = pending?.kind === "finish"
  const unanswered =
    pendingRound != null && pendingRound.answered < pendingRound.total
  const compare =
    selected.length === 2 ? (
      <Button
        variant="outline"
        className="h-9 shrink-0 px-4"
        render={
          <Link href={`/rounds/compare?a=${selected[0]}&b=${selected[1]}`} />
        }
        nativeButton={false}
      >
        {t("compare")}
      </Button>
    ) : (
      <Button variant="outline" className="h-9 shrink-0 px-4" disabled>
        {t("compare")}
      </Button>
    )

  return (
    <div className="space-y-8">
      <div className="relative">
        {back}
        <div className="flex items-center justify-between gap-4">
          <div className="min-w-0">{title}</div>
          {items.length > 0 && compare}
        </div>
      </div>
      {items.length === 0 && (
        <p className="py-16 text-center text-muted-foreground">
          {t("noRounds")}
        </p>
      )}
      {items.length > 0 && (
        <VirtualList
          items={items}
          getKey={(round) => round.id}
          estimateSize={89}
          onEndReached={loadMore}
          className="divide-y rounded-2xl border"
          renderItem={(round) => {
            const finished = round.status === "finished"
            const score = finished ? round.final_score : round.current_score

            return (
              <div className="flex flex-wrap items-center gap-2 p-3 transition-colors hover:bg-muted/50 sm:flex-nowrap sm:gap-4 sm:p-4">
                <div className="p-3">
                  <Checkbox
                    className="size-6 [&_[data-slot=checkbox-indicator]>svg]:size-4"
                    disabled={!finished}
                    checked={selected.includes(round.id)}
                    onCheckedChange={(checked) => toggle(round.id, checked)}
                    aria-label={t("selectToCompare")}
                  />
                </div>
                <Link
                  href={`/rounds/${round.id}`}
                  className="min-w-0 flex-1 space-y-1"
                >
                  <span className="block text-lg font-medium">
                    <time dateTime={round.started_at} suppressHydrationWarning>
                      {formatDate(round.started_at, locale)}
                    </time>
                  </span>
                  <span className="block text-sm text-muted-foreground">
                    {t("answeredOf", {
                      answered: round.answered,
                      total: round.total,
                    })}
                  </span>
                </Link>
                {score != null && (
                  <div
                    className={cn(
                      "flex shrink-0 items-baseline gap-2",
                      !finished && "me-2 sm:me-4"
                    )}
                  >
                    {!finished && (
                      <span className="text-xs text-muted-foreground">
                        {t("grade")}
                      </span>
                    )}
                    <span
                      className={cn(
                        "text-2xl font-light tabular-nums",
                        round.passed
                          ? "text-green-600 dark:text-green-400"
                          : "text-red-600 dark:text-red-400"
                      )}
                    >
                      {score}%
                    </span>
                  </div>
                )}
                {!finished && (
                  <div className="flex shrink-0 items-center gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      nativeButton={false}
                      render={<Link href={`/rounds/${round.id}`} />}
                    >
                      {t("continue")}
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() =>
                        setPending({ id: round.id, kind: "finish" })
                      }
                    >
                      {t("finish")}
                    </Button>
                  </div>
                )}
                <div className="p-3">
                  <Button
                    variant="ghost"
                    size="icon"
                    aria-label={t("deleteRound")}
                    className="size-12 text-muted-foreground hover:text-destructive"
                    onClick={() => setPending({ id: round.id, kind: "delete" })}
                  >
                    <Trash2Icon className="size-6" />
                  </Button>
                </div>
              </div>
            )
          }}
        />
      )}
      <Dialog
        open={pending !== null}
        onOpenChange={(open) => {
          if (!open && !busy) {
            setPending(null)
          }
        }}
      >
        <DialogContent showCloseButton={false}>
          <DialogHeader>
            <DialogTitle className="no-dot">
              {finishing ? t("finishTitle") : t("deleteTitle")}
            </DialogTitle>
            <DialogDescription>
              {finishing
                ? unanswered
                  ? t("unscored")
                  : t("noMore")
                : t("cantUndo")}
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <DialogClose
              render={
                <Button
                  variant="outline"
                  className="h-10 px-5 text-base"
                  disabled={busy}
                />
              }
            >
              {common("cancel")}
            </DialogClose>
            <Button
              variant={finishing ? "default" : "destructive"}
              className="h-10 px-5 text-base"
              disabled={busy}
              onClick={confirm}
            >
              {finishing ? t("finish") : common("delete")}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
