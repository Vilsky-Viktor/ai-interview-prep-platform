import { GlobeIcon, LockIcon, StarIcon } from "lucide-react"
import { getTranslations } from "next-intl/server"

import {
  LandingSection,
  MoreLink,
  PANEL,
  Stage,
} from "@/components/landing/section"

export async function ShareSection() {
  const t = await getTranslations("landing.share")
  const topics = await getTranslations("landing.control.topics")

  const browse = <MoreLink href="/library">{t("browse")}</MoreLink>

  return (
    <LandingSection title={t("title")} text={t("text")} extra={browse}>
      <Stage>
        <ul className={`${PANEL} divide-y divide-border/70`}>
          <li className="flex items-center justify-between gap-3 px-6 py-5 text-base">
            <div className="space-y-1">
              <p>{topics("design")}</p>
              <p className="flex items-center gap-1.5 text-sm text-muted-foreground">
                <LockIcon className="size-3.5" />
                {t("private")}
              </p>
            </div>
            <div className="flex -space-x-2 rtl:space-x-reverse">
              {["A", "M", "K"].map((letter) => (
                <span
                  key={letter}
                  className="flex size-8 items-center justify-center rounded-full bg-muted text-xs ring-2 ring-background"
                >
                  {letter}
                </span>
              ))}
            </div>
          </li>
          <li className="flex items-center justify-between gap-3 px-6 py-5 text-base">
            <div className="space-y-1">
              <p>{topics("sql")}</p>
              <p className="flex items-center gap-1.5 text-sm text-muted-foreground">
                <GlobeIcon className="size-3.5" />
                {t("public")}
              </p>
            </div>
            <div className="flex gap-0.5 text-primary">
              {[1, 2, 3, 4, 5].map((star) => (
                <StarIcon key={star} className="size-4 fill-current" />
              ))}
            </div>
          </li>
        </ul>
      </Stage>
    </LandingSection>
  )
}
