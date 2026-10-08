import { cn } from "cn"
import { PlayIcon } from "lucide-react"
import { getTranslations } from "next-intl/server"

import { buttonVariants } from "@/components/ui/button"
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip"
import { DEMOS_URL } from "@/constants/landing"

/** "demos": prepza's demo videos on YouTube, in a new tab, as an outline button with a play icon
 * and a tooltip saying where it leads. */
export async function DemosButton({ className }: { className?: string }) {
  const t = await getTranslations("landing")

  return (
    <Tooltip>
      <TooltipTrigger
        render={
          <a
            href={DEMOS_URL}
            target="_blank"
            rel="noopener noreferrer"
            className={cn(
              buttonVariants({ variant: "outline" }),
              "h-12 gap-2 border-foreground/20 px-6 text-base lowercase dark:border-input",
              className
            )}
          />
        }
      >
        <PlayIcon aria-hidden className="size-5" />
        {t("demos")}
      </TooltipTrigger>
      <TooltipContent>{t("demosTooltip")}</TooltipContent>
    </Tooltip>
  )
}
