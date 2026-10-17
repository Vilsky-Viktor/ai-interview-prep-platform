"use client"

import { PlayIcon, XIcon } from "lucide-react"
import { useTranslations } from "next-intl"

import { OUTLINE_BUTTON } from "@/components/landing/section"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { HERO_VIDEO_ID } from "@/constants/landing"

/** "video": prepza's video in a window on the page, played by YouTube's no-cookie player, which
 * loads only once the window opens. */
export function VideoButton() {
  const t = useTranslations("landing")
  const common = useTranslations("common")

  return (
    <Dialog>
      <DialogTrigger
        render={
          <Button
            variant="outline"
            data-testid="video-button"
            className={`${OUTLINE_BUTTON} h-12 px-6 lowercase`}
          />
        }
      >
        <PlayIcon aria-hidden className="size-5" />
        {t("demos")}
      </DialogTrigger>
      {/* The close button sits on the window's corner, over its edge; on phones, where the
          window spans the screen, inside it. */}
      <DialogContent
        showCloseButton={false}
        className="sm:max-w-4xl sm:overflow-visible"
        bodyClassName="gap-0 px-4 pt-16 pb-4 sm:p-6"
      >
        <DialogClose
          render={
            <Button
              variant="outline"
              size="icon"
              className="absolute end-3 top-3 z-10 size-11 rounded-full bg-popover sm:-end-5 sm:-top-5 dark:bg-popover"
            />
          }
        >
          <XIcon className="size-6" />
          <span className="sr-only">{common("close")}</span>
        </DialogClose>
        <DialogTitle className="sr-only">{t("demos")}</DialogTitle>
        <iframe
          src={`https://www.youtube-nocookie.com/embed/${HERO_VIDEO_ID}?autoplay=1&rel=0`}
          title={t("demos")}
          allow="autoplay; encrypted-media; picture-in-picture; fullscreen"
          allowFullScreen
          className="aspect-video w-full rounded-lg"
        />
      </DialogContent>
    </Dialog>
  )
}
