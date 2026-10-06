import { cn } from "cn"
import { InfoIcon } from "lucide-react"
import { getTranslations } from "next-intl/server"

import { serverFetch } from "@/lib/server-api"

/** While prepza is paused (the admin zone's emergency pause), the gray info card says so;
 * otherwise nothing. */
export async function PausedNotice({ className }: { className?: string }) {
  const t = await getTranslations("pause")
  const pause = await serverFetch<{ paused: boolean }>("/companies/pause")

  if (!pause?.paused) {
    return null
  }

  return (
    <div
      role="status"
      className={cn(
        "flex items-center gap-3 rounded-2xl border bg-muted px-5 py-4 text-base text-muted-foreground",
        className
      )}
    >
      <InfoIcon aria-hidden className="size-6 shrink-0 text-primary" />
      <p>{t("notice")}</p>
    </div>
  )
}
