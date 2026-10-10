import Link from "next/link"
import { useTranslations } from "next-intl"

import { AiAppsInstructions } from "@/components/company/ai-apps-setup"
import { Badge } from "@/components/ui/badge"
import { MCP_MARK } from "@/constants/ai-apps"
import type { AiConnection } from "@/types/connections"
import {
  INTEGRATION_LINK,
  INTEGRATION_LOGO,
  INTEGRATION_ROW,
} from "@/constants/lists"

/** AI apps' row on the integrations tab, laid out like the API's: the MCP mark, the name, and
 * which apps the user connected ("connected" beside the name when any); the row opens their page, its Instructions on top. */
export function AiAppsRow({
  companyId,
  connections,
}: {
  companyId: string
  connections: AiConnection[]
}) {
  const t = useTranslations("aiApps")
  const ats = useTranslations("ats")
  const names = [...new Set(connections.map((item) => item.client_name))]

  return (
    <li className={INTEGRATION_ROW}>
      <Link
        href={`/companies/${companyId}/integrations/ai`}
        className={INTEGRATION_LINK}
      >
        <span className={INTEGRATION_LOGO + " p-7 max-sm:p-2.5"}>
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={MCP_MARK}
            alt=""
            className="size-full object-contain dark:brightness-0 dark:invert"
          />
        </span>
        <span className="min-w-0 space-y-1">
          <span className="flex items-center gap-3 text-lg font-medium">
            {t("name")}
            {names.length > 0 && (
              <Badge className="h-7 shrink-0 px-3 text-sm font-light">
                {ats("statusConnected")}
              </Badge>
            )}
          </span>
          <span className="block text-base text-muted-foreground">
            {names.length > 0 ? names.join(", ") : t("rowText")}
          </span>
        </span>
      </Link>
      {/* Its Instructions on top of the row, as Slack's buttons; on phones under the name. */}
      <span className="relative z-10 max-sm:col-span-2 max-sm:*:w-full">
        <AiAppsInstructions />
      </span>
    </li>
  )
}
