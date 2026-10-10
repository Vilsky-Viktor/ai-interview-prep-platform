import { CodeXmlIcon } from "lucide-react"
import Link from "next/link"
import { useTranslations } from "next-intl"

import { Button } from "@/components/ui/button"
import { API_DOCS_PATH } from "@/constants/api"
import type { ApiSettings } from "@/types/api-access"
import {
  INTEGRATION_LINK,
  INTEGRATION_LOGO,
  INTEGRATION_ROW,
} from "@/constants/lists"

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
    <li className={INTEGRATION_ROW}>
      <Link
        href={`/companies/${companyId}/integrations/api`}
        className={INTEGRATION_LINK}
      >
        <span className={INTEGRATION_LOGO}>
          <CodeXmlIcon className="size-10 max-sm:size-6" />
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
      {/* On phones the logo spans the row, with the name and then these buttons beside it,
          sharing their line equally (each on its own line where both don't fit). */}
      <span className="relative z-10 max-sm:col-span-2 max-sm:*:flex max-sm:*:w-full max-sm:*:flex-wrap max-sm:[&>*>*]:flex-1 max-sm:[&>*>*]:px-3">
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
