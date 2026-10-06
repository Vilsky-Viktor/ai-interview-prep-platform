import { BriefcaseBusinessIcon } from "lucide-react"
import Link from "next/link"
import { getTranslations } from "next-intl/server"

import { Button } from "@/components/ui/button"

/** For a hiring manager who found a practice interview: the main page, where they create an
 * interview for their own candidates, signed in or not. */
export async function HireWithTemplate() {
  const t = await getTranslations("practice")

  return (
    <div className="flex flex-col gap-4 rounded-2xl border p-6 sm:flex-row sm:items-center sm:justify-between">
      <div className="flex items-center gap-4">
        <BriefcaseBusinessIcon
          aria-hidden
          className="size-6 shrink-0 text-primary"
        />
        <div className="space-y-1">
          <p className="text-lg font-medium">{t("hireTitle")}</p>
          <p className="text-base text-muted-foreground">{t("hireText")}</p>
        </div>
      </div>
      <Button
        className="h-10 shrink-0 px-5 text-base"
        render={<Link href="/" />}
        nativeButton={false}
      >
        {t("hireButton")}
      </Button>
    </div>
  )
}
