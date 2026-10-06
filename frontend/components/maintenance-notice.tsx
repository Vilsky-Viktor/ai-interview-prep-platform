import { TriangleAlertIcon } from "lucide-react"
import { headers } from "next/headers"
import { getTranslations } from "next-intl/server"

import { MAINTENANCE_HEADER } from "@/constants/maintenance"

/** While maintenance mode is on, superadmins still see the site, with a warning card above
 * every page saying so (the design of the AI-written warning in TopicQuestions); otherwise
 * nothing. Its negative bottom margin takes the page's top padding (py-12) down to the gap
 * between a title and what's right under it (space-y-4). */
export async function MaintenanceNotice() {
  if ((await headers()).get(MAINTENANCE_HEADER) !== "open") {
    return null
  }

  const t = await getTranslations("maintenance")

  return (
    <div className="mx-auto -mb-8 max-w-5xl px-6 pt-6">
      <div
        role="status"
        className="flex items-center gap-4 rounded-2xl bg-muted p-5 text-base"
      >
        <TriangleAlertIcon
          aria-hidden
          className="size-7 shrink-0 text-amber-600 dark:text-amber-400"
        />
        <p className="text-muted-foreground">{t("notice")}</p>
      </div>
    </div>
  )
}
