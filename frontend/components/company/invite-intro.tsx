"use client"

import { cn } from "cn"
import Link from "next/link"
import { useTranslations } from "next-intl"
import type { ReactNode } from "react"

import { CompanyLogo } from "@/components/company/company-logo"
import { VerifiedBadge } from "@/components/company/verified-badge"

/** What a candidate sees before starting: who invited them, the test, the time per question and
 * the rules, then `action` (the start button). A company member's preview shows the same. */
export function InviteIntro({
  company,
  logoUrl,
  verifiedDomain,
  title,
  questionSeconds,
  finished,
  action,
}: {
  company: string
  // The inviting company's logo, above who invited them.
  logoUrl?: string | null
  // Its verified domain: the badge beside its name.
  verifiedDomain?: string | null
  title: string | null
  questionSeconds: number
  finished: boolean
  action: ReactNode
}) {
  const t = useTranslations("invite")

  const header = (
    <div className="space-y-4">
      {/* The logo, with who invited them on its right (under it, on phones), centered together. */}
      {company && (
        <div className="flex items-center justify-center gap-4 max-sm:flex-col">
          {logoUrl && (
            <CompanyLogo
              url={logoUrl}
              name={company}
              className="h-20 w-auto max-w-40 shrink-0 rounded-2xl object-contain"
            />
          )}
          <p
            className={cn(
              "text-base text-muted-foreground",
              logoUrl && "text-start max-sm:text-center"
            )}
          >
            {t.rich("invitedYou", {
              company,
              b: (chunks) => (
                <span className="font-medium text-foreground">
                  {chunks}
                  {verifiedDomain && (
                    <VerifiedBadge
                      domain={verifiedDomain}
                      className="ms-1 size-4"
                    />
                  )}
                </span>
              ),
            })}
          </p>
        </div>
      )}
      <h1
        className={cn(
          "font-heading text-3xl leading-[1.15] font-medium tracking-tight text-balance sm:text-4xl sm:leading-[1.15]",
          title && "normal-case"
        )}
      >
        {title ?? t("fallbackTitle")}
      </h1>
    </div>
  )

  if (finished) {
    return (
      <div className="w-full space-y-8 text-center">
        {header}
        <p className="text-base text-muted-foreground">{t("finished")}</p>
      </div>
    )
  }

  // The test and its start on the left, the rules on the right; stacked on phones, the start
  // after the rules.
  return (
    <div className="grid w-full items-center gap-10 max-md:text-center md:grid-cols-2 md:gap-16">
      <div className="space-y-8 text-center max-md:contents">
        {header}
        <p className="text-base text-muted-foreground">
          {t("timePerQuestion")}
          <span className="block">
            <span className="text-3xl font-medium text-foreground tabular-nums">
              {questionSeconds}
            </span>{" "}
            {t("secondsUnit")}
          </span>
        </p>
        <div className="max-md:order-last">{action}</div>
      </div>
      {/* The rules in a gray card, numbered in the brand color; on phones it spans the screen,
          with square corners. */}
      <ol className="-mx-6 space-y-4 bg-muted p-8 text-start text-base text-muted-foreground sm:mx-0 sm:rounded-2xl sm:p-10">
        {[
          t("pickOne"),
          t("changePick"),
          t("timeRunsOut"),
          t("unanswered"),
          t("saved"),
          // Accommodations, and the human decision behind the score.
          t("extraTime", { company: company || t("theCompany") }),
          t("people", { company: company || t("theCompany") }),
          t.rich("stay", {
            link: (chunks) => (
              <Link href="/privacy" className="underline underline-offset-4">
                {chunks}
              </Link>
            ),
          }),
        ].map((rule, index) => (
          <li key={index} className="flex items-baseline gap-4">
            <span className="w-6 shrink-0 text-xl font-medium text-primary tabular-nums">
              {index + 1}.
            </span>
            <span>{rule}</span>
          </li>
        ))}
      </ol>
    </div>
  )
}
