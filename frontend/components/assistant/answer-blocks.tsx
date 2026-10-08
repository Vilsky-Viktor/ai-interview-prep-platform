"use client"

import { cn } from "cn"
import { ArrowUpRightIcon } from "lucide-react"
import { useLocale, useTranslations } from "next-intl"

import {
  CandidateRow,
  type CandidateRowData,
} from "@/components/company/candidate-row"
import { InterviewSummary } from "@/components/company/interview-summary"
import { LocalizedLink } from "@/components/localized-link"
import { SignInOptions } from "@/components/sign-in-options"
import { Button } from "@/components/ui/button"
import { answerParts, linkPage } from "@/lib/assistant"
import type { AssistantBlock } from "@/types/assistant"

type Item = Record<string, unknown>

/** An interview, as the interview list shows it. */
function InterviewItem({ item }: { item: Item }) {
  const t = useTranslations("interviews")

  return (
    <InterviewSummary
      title={(item.title as string | null) ?? t("fallbackTitle")}
      createdAt={item.created_at as string}
      status={(item.status as string | null) ?? null}
      candidateCount={(item.candidate_count as number | undefined) ?? 0}
    />
  )
}

/** A balance: the company's name when there are several, and its credits (amber when low), as
 * the company's header shows them. */
function CreditsItem({ item }: { item: Item }) {
  const t = useTranslations("company")
  const locale = useLocale()
  const available = item.available as number

  return (
    <>
      <span className="min-w-0 truncate text-lg font-medium">
        {item.name as string | undefined}
      </span>
      <span className="shrink-0 text-base text-muted-foreground">
        <span
          className={cn(
            "font-medium text-foreground tabular-nums",
            Boolean(item.low) && "text-amber-600 dark:text-amber-400"
          )}
        >
          {available.toLocaleString(locale)}
        </span>{" "}
        {t("creditsLeft", { count: available })}
      </span>
    </>
  )
}

const ROW = "flex items-center justify-between gap-4 p-4"
// The blocks showing candidates: a list, or one candidate's results.
const CANDIDATE_KINDS = ["candidate_rows", "scorecard_summary"]

/** One item of a block, opening its page when it has one. */
function BlockRow({
  kind,
  item,
  href,
  onNavigate,
}: {
  kind: AssistantBlock["kind"]
  item: Item
  href: string | null
  onNavigate: () => void
}) {
  if (CANDIDATE_KINDS.includes(kind)) {
    return (
      href && (
        <CandidateRow
          candidate={item as CandidateRowData}
          href={href}
          onClick={onNavigate}
        />
      )
    )
  }

  const content =
    kind === "interview" ? (
      <InterviewItem item={item} />
    ) : (
      <CreditsItem item={item} />
    )

  if (!href) {
    return <div className={ROW}>{content}</div>
  }

  return (
    <LocalizedLink
      href={href}
      onClick={onNavigate}
      className={cn(ROW, "transition-colors hover:bg-muted/50")}
    >
      {content}
    </LocalizedLink>
  )
}

/** What an answer's tools found: candidates, interviews and balances in the lists the app's
 * pages use, each opening its page, then links to the pages the rest came from, and a
 * sign-in card when a visitor asked to sign in. */
export function AnswerBlocks({
  blocks,
  onNavigate,
}: {
  blocks: AssistantBlock[]
  onNavigate: () => void
}) {
  const t = useTranslations("assistant.pages")
  const card = useTranslations("assistant")
  const { rows, links, signIn } = answerParts(blocks)

  return (
    <div className="space-y-3">
      {rows.map(
        (block, index) =>
          block.items.length > 0 && (
            <ul
              key={index}
              className="divide-y overflow-hidden rounded-2xl border"
            >
              {block.items.map(({ item, href }, row) => (
                <li key={row}>
                  <BlockRow
                    kind={block.kind}
                    item={item}
                    href={href}
                    onNavigate={onNavigate}
                  />
                </li>
              ))}
            </ul>
          )
      )}
      {signIn && (
        <div className="space-y-4 rounded-2xl border p-4">
          <p className="text-sm text-muted-foreground">{card("signInCard")}</p>
          <SignInOptions first={signIn.provider} />
        </div>
      )}
      {links.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {links.map((href) => {
            const page = linkPage(href)

            return (
              <Button
                key={href}
                variant="outline"
                size="sm"
                render={<LocalizedLink href={href} onClick={onNavigate} />}
                nativeButton={false}
              >
                {page ? t(page) : t("open")}
                <ArrowUpRightIcon
                  data-icon="inline-end"
                  className="rtl:-scale-x-100"
                />
              </Button>
            )
          })}
        </div>
      )}
    </div>
  )
}
