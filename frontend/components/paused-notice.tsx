import { cn } from "cn"
import { InfoIcon } from "lucide-react"
import { getTranslations } from "next-intl/server"

/** While prepza is paused (the admin zone's emergency pause, from isPaused), the gray info card
 * says so; otherwise nothing. */
export async function PausedNotice({
  paused,
  className,
}: {
  paused: boolean
  className?: string
}) {
  const t = await getTranslations("pause")

  if (!paused) {
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
