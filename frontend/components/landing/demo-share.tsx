"use client"

import { cn } from "cn"
import { CircleCheckIcon, DownloadIcon, Share2Icon } from "lucide-react"
import { useTranslations } from "next-intl"

import { CHAT_APPS } from "@/components/chat-apps"
import { Caret } from "@/components/landing/caret"
import { buttonVariants } from "@/components/ui/button"

// A report action's icon, like the page's icon buttons, a size down.
const ACTION =
  "flex size-10 shrink-0 items-center justify-center rounded-full text-muted-foreground transition-shadow"

/** A report's two actions, small, for the landing: download its PDF and share it; `shareRef`
 * for the pointer, the share icon `pressed` as it's clicked. */
export function DemoReportActions({
  shareRef,
  pressed,
}: {
  shareRef: React.Ref<HTMLSpanElement>
  pressed: boolean
}) {
  return (
    <span className="flex shrink-0 items-center">
      <span className={ACTION}>
        <DownloadIcon className="size-5" />
      </span>
      <span
        ref={shareRef}
        className={cn(ACTION, pressed && "bg-muted ring-3 ring-ring/50")}
      >
        <Share2Icon className="size-5" />
      </span>
    </span>
  )
}

/** The share popup, small, over the whole panel while `open`: its title and the chat apps that
 * get a text summary, the recipient's email (`email` as typed so far, a caret while `typing`),
 * then cancel and "send PDF". `pressed` names what's being clicked. */
export function DemoSharePopup({
  open,
  email,
  typing,
  pressed,
  emailRef,
  sendRef,
  whatsAppRef,
}: {
  open: boolean
  email: string
  typing: boolean
  pressed: "send" | "whatsApp" | null
  emailRef: React.Ref<HTMLDivElement>
  sendRef: React.Ref<HTMLSpanElement>
  whatsAppRef: React.Ref<HTMLSpanElement>
}) {
  const t = useTranslations("report")
  const common = useTranslations("common")

  return (
    <div
      className={cn(
        "absolute inset-0 z-5 flex items-center justify-center rounded-3xl bg-black/10 p-3 transition-opacity duration-200",
        !open && "invisible opacity-0"
      )}
    >
      <div
        className={cn(
          "w-full max-w-md space-y-5 rounded-xl bg-popover p-5 text-base text-popover-foreground ring-1 ring-foreground/10 transition-[translate,scale] duration-200 sm:p-6",
          !open && "translate-y-2.5 scale-[0.97]"
        )}
      >
        <div className="flex items-center justify-between gap-3 max-sm:flex-col">
          <p className="font-heading text-xl leading-none font-medium">
            {t("shareTitle")}
          </p>
          <div className="flex flex-wrap items-center justify-center gap-0.5">
            <span className="me-1.5 text-sm text-muted-foreground lowercase max-sm:basis-full max-sm:text-center">
              {t("orSummary")}
            </span>
            {CHAT_APPS.map(({ name, Icon }, index) => (
              <span
                key={name}
                ref={index === 0 ? whatsAppRef : undefined}
                className={cn(
                  "flex size-10 items-center justify-center rounded-full text-muted-foreground transition-shadow",
                  index === 0 &&
                    pressed === "whatsApp" &&
                    "bg-muted text-foreground ring-3 ring-ring/50"
                )}
              >
                <Icon className="size-6" />
              </span>
            ))}
          </div>
        </div>
        <div
          ref={emailRef}
          className={cn(
            "flex h-12 items-center rounded-full border bg-muted px-5 dark:bg-input/30",
            typing || email ? "border-ring" : "border-input"
          )}
        >
          {email || typing ? (
            <>
              <span className="truncate">{email}</span>
              {typing && <Caret />}
            </>
          ) : (
            <span className="truncate text-muted-foreground">
              manager@example.com
            </span>
          )}
        </div>
        <div className="flex justify-end gap-2">
          <span
            className={buttonVariants({
              variant: "outline",
              className: "h-9 px-4 text-base",
            })}
          >
            {common("cancel")}
          </span>
          <span
            ref={sendRef}
            className={buttonVariants({
              className: cn(
                "h-9 px-4 text-base transition-opacity",
                !email && "opacity-50",
                pressed === "send" && "ring-3 ring-ring/50"
              ),
            })}
          >
            <span>
              {t.rich("send", {
                name: (chunks) => <span className="normal-case">{chunks}</span>,
              })}
            </span>
          </span>
        </div>
      </div>
    </div>
  )
}

/** The notice the site shows once a report is emailed, at the panel's bottom while `shown`. */
export function DemoSentNotice({
  shown,
  email,
}: {
  shown: boolean
  email: string
}) {
  const t = useTranslations("report")

  return (
    <div
      data-testid="demo-sent"
      data-shown={shown}
      className={cn(
        "absolute inset-x-3 bottom-4 z-5 flex justify-center transition-[opacity,translate] duration-300",
        !shown && "invisible translate-y-2 opacity-0"
      )}
    >
      <p className="flex items-center gap-3 rounded-lg border bg-popover px-4 py-3 text-base text-popover-foreground">
        <CircleCheckIcon className="size-6 shrink-0" />
        <span className="min-w-0">{t("sent", { email })}</span>
      </p>
    </div>
  )
}
