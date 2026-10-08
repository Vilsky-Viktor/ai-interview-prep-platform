import { cn } from "cn"
import { ArrowRightIcon, CodeXmlIcon } from "lucide-react"
import Link from "next/link"
import { getTranslations } from "next-intl/server"

import { ApiDemo } from "@/components/landing/api-demo"
import { LandingSection } from "@/components/landing/section"
import { Button } from "@/components/ui/button"
import { API_DOCS_PATH } from "@/constants/api"
import { ATS_PROVIDERS } from "@/constants/ats"
import { SLACK } from "@/constants/slack"

const POINTS = ["move", "back", "api"] as const

/** The tools a company can connect: its ATS and Slack, as their own full logos in their colors,
 * and its own platform through the API, as an example request and the link to its docs. */
export async function AtsSection() {
  const t = await getTranslations("landing.ats")

  return (
    <LandingSection title={t("title")} text={t("text")}>
      <ul className="mx-auto mt-10 flex w-full max-w-4xl flex-wrap items-center justify-center gap-y-8">
        {[...ATS_PROVIDERS, SLACK].map((provider) => (
          <li
            key={provider.id}
            className="flex basis-1/2 justify-center px-4 sm:basis-1/3"
          >
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={provider.wordmark}
              alt={provider.name}
              className={cn(
                "h-10 w-auto max-w-full object-contain sm:h-12",
                provider.darkWhite && "dark:brightness-0 dark:invert"
              )}
            />
          </li>
        ))}
      </ul>
      <div className="mx-auto mt-8 w-full max-w-4xl">
        {/* prepza's API, named over it, and a request typed out with its answer. */}
        <div className="overflow-hidden rounded-2xl bg-muted text-sm">
          {/* The API's name, and its docs at the end of the row. */}
          <div className="flex items-center justify-between gap-4 border-b px-5 py-3">
            <p className="flex items-center gap-2 text-base font-medium">
              <CodeXmlIcon className="size-5" />
              {t("apiName")}
            </p>
            <Button
              variant="outline"
              className="h-9 px-4 text-sm"
              render={<Link href={API_DOCS_PATH} />}
              nativeButton={false}
            >
              {t("docs")}
              <ArrowRightIcon className="size-4 rtl:-scale-x-100" />
            </Button>
          </div>
          {/* Code, so it reads left to right in every language. */}
          <div dir="ltr">
            <ApiDemo />
          </div>
        </div>
      </div>
      <ul className="mx-auto mt-8 grid w-full max-w-5xl gap-x-10 gap-y-3 text-muted-foreground sm:grid-cols-3">
        {POINTS.map((point) => (
          <li key={point} className="flex gap-3">
            <span className="mt-2.5 size-1.5 shrink-0 rounded-full bg-primary" />
            <span>{t(`points.${point}`)}</span>
          </li>
        ))}
      </ul>
    </LandingSection>
  )
}
