import { DownloadIcon } from "lucide-react"
import Link from "next/link"
import { getLocale, getTranslations } from "next-intl/server"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { DOCUMENTS } from "@/constants/documents"
import { DEFAULT_LOCALE } from "@/constants/i18n"
import { pageMetadata } from "@/lib/site"
import { LIST_BOX } from "@/constants/lists"

// Like the report's download button (components/company/report-actions.tsx).
const ICON_BUTTON =
  "size-12 shrink-0 text-muted-foreground hover:text-foreground"

export async function generateMetadata() {
  const t = await getTranslations("docs")

  return pageMetadata(t("metaTitle"), t("intro"), "/documents", true)
}

/** Documents for companies to download: instructions, notice and DPIA templates, the DPA. */
export default async function DocsPage() {
  const t = await getTranslations("docs")
  const locale = await getLocale()

  return (
    <main className="mx-auto max-w-5xl space-y-8 px-6 py-12">
      <header className="space-y-4">
        <h1 className="font-heading text-3xl font-medium tracking-tight">
          {t("title")}
        </h1>
        <p className="text-base text-muted-foreground">
          {t("intro")}
          {/* The documents are English only, like the legal pages. */}
          {locale !== DEFAULT_LOCALE && (
            <span className="block pt-2 text-sm">{t("englishOnly")}</span>
          )}
        </p>
      </header>
      <ul className={`${LIST_BOX} overflow-hidden`}>
        {DOCUMENTS.map((item) => (
          <li
            key={item.key}
            className="flex items-center justify-between gap-4 py-6 ps-6 pe-3"
          >
            <div className="min-w-0 space-y-1">
              <span className="block text-xl font-medium">
                {t(`items.${item.key}.title`)}
              </span>
              <p className="text-sm text-muted-foreground">
                {t(`items.${item.key}.description`)}
                {"online" in item && (
                  <>
                    {" "}
                    <Link
                      href={item.online}
                      className="underline underline-offset-4 hover:text-foreground"
                    >
                      {t("readOnline")}
                    </Link>
                  </>
                )}
              </p>
            </div>
            {/* The format beside the download button; above it, on phones. */}
            <div className="flex shrink-0 items-center gap-2 max-sm:flex-col max-sm:gap-1">
              <Badge
                variant="secondary"
                className="h-7 px-3 text-sm font-light"
              >
                {item.format}
              </Badge>
              <Button
                variant="ghost"
                size="icon"
                className={ICON_BUTTON}
                aria-label={t("download", { format: item.format })}
                render={<a href={item.href} download />}
                nativeButton={false}
              >
                <DownloadIcon className="size-6" />
              </Button>
            </div>
          </li>
        ))}
      </ul>
    </main>
  )
}
