import { ArrowRightIcon, CopyIcon } from "lucide-react"
import { getTranslations } from "next-intl/server"
import { Fragment } from "react"

import { LandingSection, Stage } from "@/components/landing/section"
import { serverFetch } from "@/lib/server-api"
import { siteUrl } from "@/lib/site"
import type { Catalog } from "@/types/billing"

// The picture's two referral links, as billing makes their codes, and how often each has paid off.
const LINKS = [
  { side: "learner", path: "/", code: "k7Qm2xPa", rewarded: 3 },
  { side: "company", path: "/company", code: "Hc3vR9tL", rewarded: 2 },
] as const

/** The referral links as they really look (components/billing/referral-link.tsx), side by side:
 * a learner's from Settings, and a company's from its referrals tab. The rewards come from
 * billing. */
export async function ReferralsSection() {
  const t = await getTranslations("landing.referrals")
  const referral = await getTranslations("referral")
  const menu = await getTranslations("userMenu")
  const settings = await getTranslations("settings")
  const nav = await getTranslations("nav")
  const company = await getTranslations("company")
  const catalog = await serverFetch<Catalog>("/billing/catalog")
  const host = siteUrl().replace(/^https?:\/\//, "")

  if (!catalog) {
    return null
  }

  const headings = {
    learner: {
      title: referral("title"),
      note: referral("note", { reward: catalog.referral_user }),
      // Where the link is, named with the menus' own labels.
      where: t("whereLearner", {
        settings: menu("settings"),
        referral: settings("referral"),
      }),
    },
    company: {
      title: referral("companyTitle"),
      note: referral("companyNote", {
        reward: catalog.referral_company,
        min: catalog.referral_company_min_dollars,
      }),
      where: t("whereCompany", {
        hiring: nav("hiring"),
        referrals: company("referrals"),
      }),
    },
  }

  return (
    <LandingSection title={t("title")} text={t("text")}>
      <Stage wide>
        {/* The cards share a row, so they line up when one note runs a line longer. */}
        <div className="grid grid-cols-1 gap-8 text-start md:grid-cols-2 md:grid-rows-[auto_auto_auto] md:gap-x-5">
          {LINKS.map(({ side, path, code, rewarded }) => (
            <div
              key={side}
              className="grid min-w-0 grid-cols-1 gap-3 md:row-span-3 md:grid-rows-subgrid"
            >
              <div className="space-y-1">
                <p className="font-heading text-lg font-medium tracking-tight lowercase">
                  {headings[side].title}
                  <span className="text-primary">.</span>
                </p>
                <p className="text-sm text-muted-foreground">
                  {headings[side].note}
                </p>
              </div>
              <div className="space-y-6 rounded-2xl border bg-background p-6">
                <div className="relative">
                  <p className="truncate rounded-full bg-muted py-5 ps-6 pe-20 text-lg dark:bg-input/30">
                    {host}
                    {path}?ref={code}
                  </p>
                  <span className="absolute inset-y-0 end-3 my-auto flex size-10 items-center justify-center rounded-full bg-primary text-primary-foreground">
                    <CopyIcon className="size-5" />
                  </span>
                </div>
                <p className="text-center text-sm text-muted-foreground">
                  {referral("rewarded", { count: rewarded })}
                </p>
              </div>
              <p className="text-sm text-muted-foreground">
                {/* Each "→" in the path is drawn as an arrow, mirrored in right-to-left languages. */}
                {headings[side].where.split("→").map((part, index) => (
                  <Fragment key={index}>
                    {index > 0 && (
                      <ArrowRightIcon className="inline size-3.5 align-[-2px] text-primary rtl:-scale-x-100" />
                    )}
                    {part}
                  </Fragment>
                ))}
              </p>
            </div>
          ))}
        </div>
      </Stage>
    </LandingSection>
  )
}
