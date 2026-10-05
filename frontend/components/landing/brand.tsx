import { getTranslations } from "next-intl/server"

import { VerifiedBadge } from "@/components/company/verified-badge"
import { DemoLogo } from "@/components/landing/demo-logo"
import { LandingSection, PANEL, Stage } from "@/components/landing/section"

const POINTS = ["email", "interview", "report", "verified"] as const

/** A candidate's invitation as they see it (components/company/invite-intro.tsx): the
 * company's logo and its verified check. */
export async function BrandSection() {
  const t = await getTranslations("landing.brand")
  const invite = await getTranslations("invite")

  return (
    <LandingSection title={t("title")} text={t("text")}>
      <Stage>
        <div className={`${PANEL} space-y-4 px-5 py-10 text-center sm:px-10`}>
          <div className="flex items-center justify-center gap-4">
            <DemoLogo className="size-16" />
            <p className="text-start text-base text-muted-foreground">
              {invite.rich("invitedYou", {
                company: "Acme",
                b: (chunks) => (
                  <span className="font-medium text-foreground">
                    {chunks}
                    <VerifiedBadge domain="acme.com" className="ms-1 size-4" />
                  </span>
                ),
              })}
            </p>
          </div>
          <p className="font-heading text-3xl font-medium tracking-tight">
            {t("role")}
          </p>
        </div>
      </Stage>
      <ul className="mx-auto grid w-full max-w-2xl gap-x-8 gap-y-3 text-muted-foreground sm:grid-cols-2">
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
