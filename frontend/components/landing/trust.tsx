import {
  BotOffIcon,
  CalendarX2Icon,
  CreditCardIcon,
  DownloadIcon,
  FileTextIcon,
  HourglassIcon,
  KeyRoundIcon,
  ListChecksIcon,
  UserCheckIcon,
} from "lucide-react"
import { getTranslations } from "next-intl/server"

import { LandingSection, MoreLink } from "@/components/landing/section"

// The section's points, each with its icon, in the price cards' design (pricing.tsx). Only
// what's true today; every one is checked against the code or the privacy policy.
const POINTS = [
  { key: "decision", Icon: UserCheckIcon },
  { key: "key", Icon: KeyRoundIcon },
  { key: "training", Icon: BotOffIcon },
  { key: "time", Icon: HourglassIcon },
  { key: "notice", Icon: ListChecksIcon },
  { key: "own", Icon: DownloadIcon },
  { key: "data", Icon: CalendarX2Icon },
  { key: "payments", Icon: CreditCardIcon },
  { key: "documents", Icon: FileTextIcon },
] as const

// Where a company checks it all.
const LINKS = [
  { key: "see", href: "/documents" },
  { key: "terms", href: "/terms" },
  { key: "privacy", href: "/privacy" },
] as const

/** What makes prepza fair to candidates and safe for a company's data: no compliance claims
 * or badges, and the documents to check it. */
export async function TrustSection() {
  const t = await getTranslations("landing.trust")

  return (
    <LandingSection title={t("title")} text={t("text")}>
      <ul className="mx-auto grid w-full max-w-5xl gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {POINTS.map(({ key, Icon }) => (
          <li
            key={key}
            className="flex items-center gap-4 rounded-2xl border bg-background p-6"
          >
            <Icon aria-hidden className="size-6 shrink-0 text-primary" />
            <span className="text-base whitespace-pre-line">
              {t(`points.${key}`)}
            </span>
          </li>
        ))}
      </ul>
      <div className="flex flex-wrap justify-center gap-3">
        {LINKS.map(({ key, href }) => (
          <MoreLink key={key} href={href}>
            {t(key)}
          </MoreLink>
        ))}
      </div>
    </LandingSection>
  )
}
