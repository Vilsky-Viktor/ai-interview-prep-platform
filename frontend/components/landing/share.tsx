import { GlobeIcon, LockIcon, StarIcon } from "lucide-react"
import Link from "next/link"
import { getTranslations } from "next-intl/server"

import { LandingSection, Mockup } from "@/components/landing/section"
import { Button } from "@/components/ui/button"

export async function ShareSection() {
  const t = await getTranslations("landing.share")
  const topics = await getTranslations("landing.control.topics")

  const browse = (
    <Button
      variant="outline"
      className="h-10 px-5 text-base"
      render={<Link href="/library" />}
      nativeButton={false}
    >
      {t("browse")}
    </Button>
  )

  return (
    <LandingSection title={t("title")} text={t("text")} extra={browse} reverse>
      <Mockup>
        <div className="flex items-center justify-between gap-3 rounded-2xl bg-muted/60 p-4">
          <div className="space-y-1">
            <p className="text-sm font-medium">{topics("design")}</p>
            <p className="flex items-center gap-1.5 text-xs text-muted-foreground">
              <LockIcon className="size-3.5" />
              {t("private")}
            </p>
          </div>
          <div className="flex -space-x-2 rtl:space-x-reverse">
            {["A", "M", "K"].map((letter) => (
              <span
                key={letter}
                className="flex size-8 items-center justify-center rounded-full bg-primary/15 text-xs font-medium text-primary ring-2 ring-card"
              >
                {letter}
              </span>
            ))}
          </div>
        </div>
        <div className="flex items-center justify-between gap-3 rounded-2xl bg-muted/60 p-4">
          <div className="space-y-1">
            <p className="text-sm font-medium">{topics("sql")}</p>
            <p className="flex items-center gap-1.5 text-xs text-muted-foreground">
              <GlobeIcon className="size-3.5" />
              {t("public")}
            </p>
          </div>
          <div className="flex text-primary">
            {[1, 2, 3, 4, 5].map((star) => (
              <StarIcon key={star} className="size-4 fill-current" />
            ))}
          </div>
        </div>
      </Mockup>
    </LandingSection>
  )
}
