import { CodeXmlIcon } from "lucide-react"
import Link from "next/link"
import { useTranslations } from "next-intl"

import { Button } from "@/components/ui/button"
import { API_DOCS_PATH } from "@/constants/api"
import type { ApiSettings } from "@/types/api-access"

/** The API's row on the integrations tab, laid out like Slack's: its mark, name, and how many keys
 * and web hooks the company has; the row opens the API page, the docs button sits on top. */
export function ApiRow({
  companyId,
  settings,
}: {
  companyId: string
  settings: ApiSettings
}) {
  const t = useTranslations("api")
  const inUse = settings.keys.length > 0

  return (
    <li className="relative flex items-center justify-between gap-6 py-6 pe-4 transition-colors hover:bg-muted/50 sm:pe-6">
      <Link
        href={`/companies/${companyId}/integrations/api`}
        className="flex min-w-0 items-center gap-4 after:absolute after:inset-0"
      >
        <span className="-my-6 me-2 flex size-[6.25rem] shrink-0 items-center justify-center bg-muted">
          <CodeXmlIcon className="size-10" />
        </span>
        <span className="min-w-0 space-y-1">
          <span className="flex items-center gap-3 text-lg font-medium">
            {t("name")}
          </span>
          <span className="block text-base text-muted-foreground">
            {inUse
              ? t("counts", {
                  keys: settings.keys.length,
                  webhooks: settings.webhooks.length,
                })
              : t("rowText")}
          </span>
        </span>
      </Link>
      <span className="relative z-10">
        <Button
          variant="outline"
          className="h-10 px-5 text-base"
          render={<Link href={API_DOCS_PATH} />}
          nativeButton={false}
        >
          {t("docs")}
        </Button>
      </span>
    </li>
  )
}
