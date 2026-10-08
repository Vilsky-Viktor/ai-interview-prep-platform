import { DownloadIcon, Share2Icon } from "lucide-react"
import { getTranslations } from "next-intl/server"

import { CHAT_APPS } from "@/components/chat-apps"
import { ReportPdfDemo } from "@/components/landing/report-pdf-demo"
import { LandingSection, PANEL, Stage } from "@/components/landing/section"

const POINTS = ["pdf", "share"] as const
const ICON = "flex size-12 items-center justify-center rounded-lg"

/** A report's two icons, download and share, with the share popup open
 * (components/company/report-actions.tsx and share-report.tsx), and beside it the PDF of all
 * candidates. */
export async function ReportsSection() {
  const t = await getTranslations("landing.reports")
  const report = await getTranslations("report")
  const common = await getTranslations("common")
  const brand = await getTranslations("landing.brand")

  return (
    <LandingSection title={t("title")} text={t("text")}>
      <Stage wide>
        <div className="grid grid-cols-1 items-center gap-6 md:grid-cols-2 [&>*]:min-w-0">
          <div className="space-y-3 text-start">
            {/* The icons as on a candidate's page; share is the one open. */}
            <div className="flex justify-end gap-1 text-muted-foreground">
              <span className={ICON}>
                <DownloadIcon className="size-6" />
              </span>
              <span className={`${ICON} bg-background text-foreground`}>
                <Share2Icon className="size-6" />
              </span>
            </div>
            <div className={`${PANEL} space-y-4 p-5 sm:p-6`}>
              <div className="flex flex-wrap items-center justify-between gap-x-4 gap-y-2">
                <p className="font-heading text-xl leading-none font-medium lowercase">
                  {report("shareTitle")}
                  <span className="text-primary">.</span>
                </p>
                <span className="ms-auto flex flex-wrap items-center justify-end gap-1 text-muted-foreground">
                  <span className="me-2 text-sm lowercase">
                    {report("orSummary")}
                  </span>
                  {CHAT_APPS.map(({ name, Icon }) => (
                    <span key={name} className={ICON}>
                      <Icon className="size-8" />
                    </span>
                  ))}
                </span>
              </div>
              <p className="flex h-16 items-center rounded-full bg-muted px-6 text-lg dark:bg-input/30">
                manager@example.com
              </p>
              <div className="flex justify-end gap-2 text-base lowercase">
                <span className="flex h-10 items-center rounded-lg border px-5">
                  {common("cancel")}
                </span>
                <span className="flex h-10 items-center rounded-lg bg-primary px-5 text-primary-foreground">
                  <span>
                    {report.rich("send", {
                      name: (chunks) => (
                        <span className="normal-case">{chunks}</span>
                      ),
                    })}
                  </span>
                </span>
              </div>
            </div>
          </div>
          <ReportPdfDemo role={brand("role")} />
        </div>
      </Stage>
      <ul className="mx-auto grid w-full max-w-2xl gap-x-8 gap-y-3 text-muted-foreground sm:grid-cols-2">
        {POINTS.map((point) => (
          <li key={point} className="flex gap-3">
            <span className="mt-2.5 size-1.5 shrink-0 rounded-full bg-primary" />
            <span>{t(`points.${point}`)}</span>
          </li>
        ))}
      </ul>
    </LandingSection>
  )
}
