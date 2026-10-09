import type { ReactNode } from "react"

/** A result's big numbers in one centered card, its halves split by a line: a test's grade, and
 * what goes with it (how many were answered, or whether it passed). */
export function GradeCard({ children }: { children: ReactNode }) {
  return (
    <div className="mx-auto flex w-fit flex-wrap items-stretch divide-x overflow-hidden rounded-2xl border">
      {children}
    </div>
  )
}

/** One half of a GradeCard: a big number (brand blue, or `tone`'s colour) and its label. */
export function GradeBlock({
  value,
  label,
  tone = "text-primary",
}: {
  value: ReactNode
  label: ReactNode
  tone?: string
}) {
  return (
    <div className="flex items-baseline gap-4 px-8 py-6">
      <p className={`text-6xl font-light tabular-nums ${tone}`}>{value}</p>
      <p className="text-base text-muted-foreground">{label}</p>
    </div>
  )
}
