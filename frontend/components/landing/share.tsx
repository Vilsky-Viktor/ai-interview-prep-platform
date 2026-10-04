import { CopyIcon } from "lucide-react"
import { getTranslations } from "next-intl/server"

import { InviteDemo } from "@/components/landing/invite-demo"
import { LandingSection, MoreLink, Stage } from "@/components/landing/section"
import {
  FacebookIcon,
  LinkedInIcon,
  SlackIcon,
  TelegramIcon,
  ThreadsIcon,
  WhatsAppIcon,
  XIcon,
} from "@/components/preparations/share-icons"
import { siteUrl } from "@/lib/site"

// The picture's invites: one person already joined, and the one the demo invites.
const INVITEE = "mark@example.com"
const PEOPLE = [{ email: "anna@example.com", joined: true }]
// The networks the public dialog offers, in its order.
const NETWORKS = [
  XIcon,
  LinkedInIcon,
  FacebookIcon,
  ThreadsIcon,
  WhatsAppIcon,
  SlackIcon,
  TelegramIcon,
]
const CARD = "space-y-5 rounded-2xl border bg-background p-6 text-start"

/** The kit page's visibility switch (visibility-toggle.tsx), drawn still, with the title of the
 * dialog under it. */
function VisibilitySwitch({ on, label }: { on: boolean; label: string }) {
  return (
    <span className="flex items-center gap-3 font-heading text-lg font-medium tracking-tight lowercase">
      <span
        className={
          on
            ? "flex h-[18.4px] w-8 items-center rounded-full bg-primary px-px"
            : "flex h-[18.4px] w-8 items-center rounded-full bg-input px-px dark:bg-input/80"
        }
      >
        <span
          className={
            on
              ? "size-4 translate-x-[calc(100%-2px)] rounded-full bg-background dark:bg-primary-foreground"
              : "size-4 rounded-full bg-background dark:bg-foreground"
          }
        />
      </span>
      <span>
        {label}
        <span className="text-primary">.</span>
      </span>
    </span>
  )
}

/** The share dialog as it really looks (components/preparations/share-dialog.tsx), side by
 * side under the kit's visibility switch: inviting people to a private kit, and sharing a public
 * one (public-share.tsx). */
export async function ShareSection() {
  const t = await getTranslations("landing.share")
  const share = await getTranslations("share")

  const browse = (
    <div className="pt-2">
      <MoreLink href="/library">{t("browse")}</MoreLink>
    </div>
  )

  return (
    <LandingSection title={t("title")} text={t("text")} extra={browse}>
      <Stage wide>
        <div className="grid gap-8 md:grid-cols-2 md:gap-5">
          <div className="min-w-0 space-y-4">
            <VisibilitySwitch on={false} label={t("private")} />
            <div className={CARD}>
              <p className="text-sm text-muted-foreground">
                {share("private")}
              </p>
              <InviteDemo
                people={PEOPLE}
                invitee={INVITEE}
                labels={{ joined: share("joined"), invited: share("invited") }}
              />
            </div>
          </div>
          <div className="min-w-0 space-y-4">
            <VisibilitySwitch on label={t("public")} />
            <div className={CARD}>
              <p className="text-sm text-muted-foreground">{share("public")}</p>
              <div className="relative">
                <p className="rounded-xl border px-5 py-5 pe-16 font-mono text-sm break-all">
                  {siteUrl().replace(/^https?:\/\//, "")}/preparations/3f8c2a
                </p>
                <span className="absolute inset-y-0 end-3 my-auto flex size-10 items-center justify-center rounded-full bg-primary text-primary-foreground">
                  <CopyIcon className="size-5" />
                </span>
              </div>
              <div className="flex flex-wrap gap-2">
                {NETWORKS.map((Icon, index) => (
                  <span
                    key={index}
                    className="flex size-10 items-center justify-center rounded-lg border [&_svg]:size-5"
                  >
                    <Icon />
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      </Stage>
    </LandingSection>
  )
}
