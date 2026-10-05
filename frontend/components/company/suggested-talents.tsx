import { InfoIcon } from "lucide-react"
import { getTranslations } from "next-intl/server"

import { HideTalent } from "@/components/company/hide-talent"
import { LinkedInIcon } from "@/components/linkedin-icon"
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip"
import { serverFetch } from "@/lib/server-api"
import type { SuggestedTalent } from "@/types/company"

/** Talents suggested for the test, free: who agreed to it and did well in their first practice
 * round on a template for a similar role. Name, LinkedIn and that score only, laid out like the
 * landing page's talent pool. A talent who doesn't fit can be hidden. */
export async function SuggestedTalents({
  interviewId,
}: {
  interviewId: string
}) {
  const t = await getTranslations("talents")
  const talents = await serverFetch<SuggestedTalent[]>(
    `/companies/interviews/${interviewId}/suggestions`
  )

  if (!talents?.length) {
    return (
      <p className="py-16 text-center text-muted-foreground">{t("empty")}</p>
    )
  }

  return (
    <div className="space-y-6">
      {/* The gray info card, like the practice test page's. */}
      <div className="flex items-center gap-3 rounded-2xl border bg-muted px-5 py-4 text-base text-muted-foreground">
        <InfoIcon aria-hidden className="size-6 shrink-0 text-primary" />
        <p>{t("about")}</p>
      </div>
      <ul className="divide-y rounded-2xl border">
        {talents.map((talent) => (
          <li key={talent.url} className="flex items-center gap-6 p-6">
            <span className="min-w-0 flex-1 truncate text-lg normal-case">
              {talent.name}
            </span>
            {/* Its own column, so the icons line up whatever the name's length. */}
            <Tooltip>
              <TooltipTrigger
                render={
                  <a
                    href={talent.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    aria-label="LinkedIn"
                    className="shrink-0 text-muted-foreground transition-colors hover:text-foreground"
                  />
                }
              >
                <LinkedInIcon />
              </TooltipTrigger>
              <TooltipContent>LinkedIn</TooltipContent>
            </Tooltip>
            <span className="w-20 shrink-0 text-center sm:w-24">
              <span className="block text-2xl font-light tabular-nums">
                {talent.grade}%
              </span>
              <span className="block text-sm text-muted-foreground">
                {t("score")}
              </span>
            </span>
            <HideTalent interviewId={interviewId} url={talent.url} />
          </li>
        ))}
      </ul>
    </div>
  )
}
