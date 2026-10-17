"use client"

import { cn } from "cn"
import { useTranslations } from "next-intl"

import { InterviewStatus } from "@/components/company/interview-status"
import { Dotted } from "@/components/dot"

/** An interview's page header, small, for the landing's pictures: its title (a size up when
 * `large`), then its `status` and size. */
export function InterviewHeader({
  title,
  topics,
  questions,
  status = "new",
  large = false,
}: {
  title: string
  topics: number
  questions: number
  status?: "new" | "in_process"
  large?: boolean
}) {
  const t = useTranslations("templates")
  const practice = useTranslations("practice")

  return (
    <div className="space-y-2 px-1 pt-1">
      <p
        className={cn(
          "font-heading font-medium",
          large ? "text-xl" : "text-base"
        )}
      >
        {title}
      </p>
      {/* On phones the size goes on its own line under the status. */}
      <div className="flex flex-wrap items-center gap-x-3 gap-y-1.5">
        <InterviewStatus status={status} />
        <span className="text-xs whitespace-nowrap text-muted-foreground max-sm:basis-full">
          <Dotted
            items={[
              t("topics", { count: topics }),
              practice("questions", { count: questions }),
            ]}
          />
        </span>
      </div>
    </div>
  )
}
