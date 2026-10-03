import { GlobeIcon, LockIcon, StarIcon } from "lucide-react"
import Link from "next/link"
import { getTranslations } from "next-intl/server"

import { LandingSection, PANEL, Stage } from "@/components/landing/section"

export async function ShareSection() {
  const t = await getTranslations("landing.share")
  const topics = await getTranslations("landing.control.topics")

  const browse = (
    <Link
      href="/library"
      className="inline-block text-primary underline-offset-4 hover:underline"
    >
      {t("browse")} →
    </Link>
  )

  return (
    <LandingSection title={t("title")} text={t("text")} extra={browse}>
      <Stage>
        <ul className={`${PANEL} divide-y divide-border/70`}>
          <li className="flex items-center justify-between gap-3 px-5 py-4">
            <div className="space-y-1">
              <p>{topics("design")}</p>
              <p className="flex items-center gap-1.5 text-xs text-muted-foreground">
                <LockIcon className="size-3" />
                {t("private")}
              </p>
            </div>
            <div className="flex -space-x-2 rtl:space-x-reverse">
              {["A", "M", "K"].map((letter) => (
                <span
                  key={letter}
                  className="flex size-7 items-center justify-center rounded-full bg-muted text-xs ring-2 ring-background"
                >
                  {letter}
                </span>
              ))}
            </div>
          </li>
          <li className="flex items-center justify-between gap-3 px-5 py-4">
            <div className="space-y-1">
              <p>{topics("sql")}</p>
              <p className="flex items-center gap-1.5 text-xs text-muted-foreground">
                <GlobeIcon className="size-3" />
                {t("public")}
              </p>
            </div>
            <div className="flex gap-0.5 text-primary">
              {[1, 2, 3, 4, 5].map((star) => (
                <StarIcon key={star} className="size-3.5 fill-current" />
              ))}
            </div>
          </li>
        </ul>
      </Stage>
    </LandingSection>
  )
}
