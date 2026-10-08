import { cn } from "cn"
import { getTranslations } from "next-intl/server"

import { VerifiedBadge } from "@/components/company/verified-badge"
import { DemoLogo } from "@/components/landing/demo-logo"
import { PdfIcon } from "@/components/pdf-icon"
import { Wordmark } from "@/components/wordmark"

const PASS_MARK = 70

// The picture's candidates, best first, as the report lists them.
const CANDIDATES = [
  { email: "anna@example.com", progress: 100, grade: 86, signals: [0, 0, 0] },
  { email: "sam@example.com", progress: 100, grade: 79, signals: [0, 0, 0] },
  { email: "mark@example.com", progress: 42, grade: 74, signals: [0, 0, 0] },
  { email: "lee@example.com", progress: 100, grade: 58, signals: [2, 1, 3] },
]

/** A page of the PDF report of all of an interview's candidates
 * (components/company/interview-report.tsx), small, always light like the real one. */
export async function ReportPdfDemo({ role }: { role: string }) {
  const t = await getTranslations("report")
  const candidates = await getTranslations("candidates")

  return (
    <div className="light-scope relative space-y-4 rounded-2xl border bg-background p-5 text-start text-foreground sm:p-6 dark:bg-[oklch(0.9_0_0)]">
      {/* It's a PDF: the file's icon in the corner. */}
      <PdfIcon className="absolute end-4 top-4 h-12 w-auto" />
      <div className="text-center">
        <Wordmark className="text-base" />
      </div>
      <div className="flex items-center gap-3">
        <DemoLogo className="size-10" />
        <div className="min-w-0 space-y-0.5">
          <p className="text-xs text-muted-foreground">
            Acme
            <VerifiedBadge domain="acme.com" className="ms-1 size-3" />
            {" · "}
            {t("candidateCount", { count: CANDIDATES.length })}
            {" · "}
            {t("passMark", { mark: PASS_MARK })}
          </p>
          <p className="font-heading text-lg font-medium tracking-tight">
            {role}
          </p>
        </div>
      </div>
      <ul className="divide-y rounded-xl border">
        {CANDIDATES.map((candidate) => {
          const [leaves, copies, fast] = candidate.signals
          // In words, as in the PDF: it has no tooltips to explain icons.
          const signals = [
            leaves && candidates("pageLeaves", { count: leaves }),
            copies && candidates("copies", { count: copies }),
            fast && candidates("fastAnswers", { count: fast }),
          ].filter(Boolean)

          return (
            <li
              key={candidate.email}
              className="flex items-center justify-between gap-3 px-3 py-2"
            >
              <div className="min-w-0">
                <p className="truncate text-sm font-medium">
                  {candidate.email}
                </p>
                {signals.length > 0 && (
                  <p className="flex flex-wrap gap-x-1.5 text-xs text-amber-600">
                    {signals.map((signal, index) => (
                      <span key={index} className="whitespace-nowrap">
                        {index > 0 && "· "}
                        {signal}
                      </span>
                    ))}
                  </p>
                )}
              </div>
              <div className="flex shrink-0 items-center gap-2">
                <Total label={candidates("progress")}>
                  {candidate.progress}%
                </Total>
                <Total
                  label={candidates("grade")}
                  className={cn(
                    candidate.progress === 100 &&
                      (candidate.grade >= PASS_MARK
                        ? "text-green-600"
                        : "text-red-600")
                  )}
                >
                  {candidate.grade}%
                </Total>
              </div>
            </li>
          )
        })}
      </ul>
    </div>
  )
}

function Total({
  label,
  className,
  children,
}: {
  label: string
  className?: string
  children: React.ReactNode
}) {
  return (
    <div className="w-16 text-center">
      <p className={cn("text-base font-light tabular-nums", className)}>
        {children}
      </p>
      <p className="text-[10px] text-muted-foreground">{label}</p>
    </div>
  )
}
