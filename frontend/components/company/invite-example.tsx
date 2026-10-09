import { useTranslations } from "next-intl"

import { INVITE_EXAMPLE_LINES } from "@/constants/invites"

/** How a list is written, in the gray info card: the hint, then example lines. */
export function InviteExample() {
  const t = useTranslations("interviews")

  return (
    <div className="space-y-2 rounded-2xl border px-5 py-4">
      <h2 className="font-heading text-lg font-medium lowercase">
        {t("example")}
      </h2>
      <p className="text-sm whitespace-pre-line text-muted-foreground">
        {t("manyHint")}
      </p>
      <p className="font-mono text-sm break-all whitespace-pre-line text-foreground/80">
        {INVITE_EXAMPLE_LINES.join("\n")}
      </p>
    </div>
  )
}
