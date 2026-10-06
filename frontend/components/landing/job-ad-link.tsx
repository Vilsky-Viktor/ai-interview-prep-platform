import { CopyIcon, LinkIcon } from "lucide-react"
import { getTranslations } from "next-intl/server"

import { LandingSection, PANEL, Stage } from "@/components/landing/section"

const POINTS = ["anywhere", "off"] as const

/** An interview's shareable link as its candidates tab shows it
 * (components/company/share-link.tsx): switched on, with the link to copy into a job ad. */
export async function JobAdLinkSection() {
  const t = await getTranslations("landing.link")
  const interviews = await getTranslations("interviews")

  return (
    <LandingSection title={t("title")} text={t("text")}>
      <Stage>
        <div className={`${PANEL} space-y-5 p-6 text-start sm:p-8`}>
          <div className="flex items-center gap-4 text-base">
            <LinkIcon className="size-7 shrink-0 text-primary" />
            <span className="min-w-0 flex-1 space-y-1">
              <span className="block font-medium lowercase">
                {interviews("linkTitle")}
              </span>
              <span className="block text-sm text-muted-foreground">
                {t("note")}
              </span>
            </span>
            {/* The switch, on. */}
            <span className="flex h-[18px] w-8 shrink-0 items-center justify-end rounded-full bg-primary p-px">
              <span className="size-4 rounded-full bg-background dark:bg-primary-foreground" />
            </span>
          </div>
          <div className="flex h-16 items-center gap-4 rounded-full bg-muted ps-6 pe-3 text-lg dark:bg-input/30">
            <span className="min-w-0 flex-1 truncate">
              https://prepza.ai/apply/k7Qm2x
            </span>
            <span className="flex size-10 shrink-0 items-center justify-center rounded-full bg-primary text-primary-foreground">
              <CopyIcon className="size-5" />
            </span>
          </div>
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
