"use client"

import { cn } from "cn"
import { BadgeQuestionMarkIcon } from "lucide-react"
import { useTranslations } from "next-intl"

import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip"
import type { PageHelpKey } from "@/types/page-help"

/** A page's info button: a muted icon that opens a short guide to the page, from
 * "pageHelp.<page>" in the messages: what it's for, what you can do there and a tip or two.
 * `className` places it; BackLink puts it under its arrow. */
export function PageHelp({
  page,
  className,
}: {
  page: PageHelpKey
  className?: string
}) {
  const t = useTranslations("pageHelp")
  const common = useTranslations("common")
  const label = t("label")
  const actions = t.raw(`${page}.actions`) as string[]
  const tips = t.raw(`${page}.tips`) as string[]

  return (
    <Dialog>
      <Tooltip>
        <TooltipTrigger
          render={
            <DialogTrigger
              render={
                <button
                  type="button"
                  aria-label={label}
                  className={cn(
                    "inline-flex size-11 shrink-0 cursor-pointer items-center justify-center rounded-xl text-muted-foreground transition-colors outline-none hover:text-foreground focus-visible:ring-3 focus-visible:ring-ring/50",
                    className
                  )}
                />
              }
            />
          }
        >
          <BadgeQuestionMarkIcon aria-hidden className="size-6" />
        </TooltipTrigger>
        <TooltipContent>{label}</TooltipContent>
      </Tooltip>
      {/* On phones it fills the screen: the guide scrolls, Close stays at the bottom. */}
      <DialogContent
        showCloseButton={false}
        className="max-h-[90dvh] gap-6 overflow-y-auto max-sm:h-dvh max-sm:max-h-dvh sm:max-w-lg"
      >
        <DialogHeader>
          <DialogTitle>{t(`${page}.title`)}</DialogTitle>
        </DialogHeader>
        <p className="text-base text-muted-foreground">{t(`${page}.text`)}</p>
        <HelpList title={t("actionsTitle")} items={actions} />
        <HelpList title={t("tipsTitle")} items={tips} />
        <DialogFooter>
          <DialogClose
            render={
              <Button variant="outline" className="h-10 px-5 text-base" />
            }
          >
            {common("close")}
          </DialogClose>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

function HelpList({ title, items }: { title: string; items: string[] }) {
  return (
    <section className="space-y-2">
      <h3 className="text-lg font-medium">{title}</h3>
      <ul className="list-disc space-y-1.5 ps-5 text-base text-muted-foreground">
        {items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </section>
  )
}
