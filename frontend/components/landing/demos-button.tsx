import { cn } from "cn"
import { PlayIcon } from "lucide-react"
import { getTranslations } from "next-intl/server"

import { buttonVariants } from "@/components/ui/button"
import { DEMOS_URL } from "@/constants/landing"

/** "demos": prepza's demo videos on YouTube, in a new tab, as an outline button with a play icon. */
export async function DemosButton({ className }: { className?: string }) {
  const t = await getTranslations("landing")

  return (
    <a
      href={DEMOS_URL}
      target="_blank"
      rel="noopener noreferrer"
      className={cn(
        buttonVariants({ variant: "outline" }),
        "h-12 gap-2 border-foreground/20 px-6 text-base lowercase dark:border-input",
        className
      )}
    >
      <PlayIcon aria-hidden className="size-5" />
      {t("demos")}
    </a>
  )
}
