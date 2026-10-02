"use client"

import { CopyIcon } from "lucide-react"
import { toast } from "sonner"

import {
  FacebookIcon,
  LinkedInIcon,
  SlackIcon,
  TelegramIcon,
  ThreadsIcon,
  WhatsAppIcon,
  XIcon,
} from "@/components/preparations/share-icons"
import { Button } from "@/components/ui/button"
import {
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { useOrigin } from "@/lib/origin"

type PublicShareProps = {
  preparationId: string
  title: string
}

function shareLinks(url: string, title: string) {
  const encodedUrl = encodeURIComponent(url)
  const encodedTitle = encodeURIComponent(title)
  const encodedText = encodeURIComponent(`${title} ${url}`)

  return [
    {
      label: "X",
      href: `https://twitter.com/intent/tweet?url=${encodedUrl}&text=${encodedTitle}`,
      icon: <XIcon />,
    },
    {
      label: "LinkedIn",
      href: `https://www.linkedin.com/sharing/share-offsite/?url=${encodedUrl}`,
      icon: <LinkedInIcon />,
    },
    {
      label: "Facebook",
      href: `https://www.facebook.com/sharer/sharer.php?u=${encodedUrl}`,
      icon: <FacebookIcon />,
    },
    {
      label: "Threads",
      href: `https://www.threads.net/intent/post?text=${encodedText}`,
      icon: <ThreadsIcon />,
    },
    {
      label: "WhatsApp",
      href: `https://api.whatsapp.com/send?text=${encodedText}`,
      icon: <WhatsAppIcon />,
    },
    {
      label: "Slack",
      href: `https://slack.com/share?url=${encodedUrl}&text=${encodedTitle}`,
      icon: <SlackIcon />,
    },
    {
      label: "Telegram",
      href: `https://t.me/share/url?url=${encodedUrl}&text=${encodedTitle}`,
      icon: <TelegramIcon />,
    },
  ]
}

export function PublicShare({ preparationId, title }: PublicShareProps) {
  const origin = useOrigin()
  const url = origin ? `${origin}/preparations/${preparationId}` : ""

  async function copy() {
    if (!url) {
      return
    }

    await navigator.clipboard.writeText(url)
    toast.success("Link copied")
  }

  return (
    <>
      <DialogHeader>
        <DialogTitle>Share preparation</DialogTitle>
        <DialogDescription>
          Anyone with the link can view this preparation.
        </DialogDescription>
      </DialogHeader>
      <div className="relative">
        <p className="rounded-lg border px-6 py-6 pr-20 font-mono text-sm break-all">
          {url}
        </p>
        <Button
          type="button"
          size="icon"
          className="absolute inset-y-0 right-3 my-auto size-10 rounded-full"
          aria-label="Copy link"
          onClick={copy}
          disabled={!url}
        >
          <CopyIcon className="size-5" />
        </Button>
      </div>
      <div className="flex flex-wrap items-center gap-2">
        {url &&
          shareLinks(url, title).map((network) => (
            <Button
              key={network.label}
              variant="outline"
              size="icon"
              className="size-12"
              nativeButton={false}
              aria-label={network.label}
              render={
                <a href={network.href} target="_blank" rel="noreferrer" />
              }
            >
              {network.icon}
            </Button>
          ))}
      </div>
    </>
  )
}
