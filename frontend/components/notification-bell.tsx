"use client"

import { cn } from "cn"
import { BellIcon } from "lucide-react"
import Link from "next/link"
import { useFormatter, useNow, useTranslations } from "next-intl"
import { useCallback, useEffect, useState } from "react"

import { useAuth } from "@/components/auth-provider"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { MAX_BADGE_COUNT, NOTIFICATION_LOOKS } from "@/constants/notifications"
import { apiFetch } from "@/lib/api"
import { watchNotifications } from "@/lib/notifications"
import type { AppNotification, NotificationFeed } from "@/types/notifications"

/** One notification's text: its kind's message, filled with what the service sent. Missing
 * values become "none", which the messages' selects read as "leave it out". */
function useNotificationText() {
  const t = useTranslations("notifications.kinds")
  const format = useFormatter()

  return (item: AppNotification) => {
    const data = item.data as Record<string, string | number | undefined>
    const values = {
      title: data.title ?? "none",
      topic: data.topic ?? "",
      email: data.email ?? "",
      grade: data.grade ?? "none",
      name: data.name ?? "",
      domain: data.domain ?? "",
      reason: data.reason ?? "none",
      // How many came together, for the kinds the service groups.
      count: typeof data.count === "number" ? data.count : 1,
      credits:
        typeof data.credits === "number" ? format.number(data.credits) : "",
    }

    return t.has(item.kind) ? t(item.kind, values) : null
  }
}

/** The bell next to the account menu: the latest notifications, live, with a count of those
 * not yet seen. Opening it counts them as seen. */
export function NotificationBell() {
  const t = useTranslations("notifications")
  const { user } = useAuth()
  const format = useFormatter()
  // Re-renders each minute, so "2 minutes ago" keeps up.
  const now = useNow({ updateInterval: 60000 })
  const text = useNotificationText()
  const [feed, setFeed] = useState<NotificationFeed | null>(null)

  const load = useCallback(() => {
    apiFetch<NotificationFeed>("/notifications/me")
      .then(setFeed)
      .catch(() => {})
  }, [])

  // Live while signed in: the stream says when something new came, and each (re)connect
  // reloads, so nothing that came while it was down is missed.
  useEffect(() => {
    if (!user) {
      return
    }

    const controller = new AbortController()
    void watchNotifications(controller.signal, load, load)

    return () => controller.abort()
  }, [user, load])

  if (!user || feed === null) {
    return null
  }

  const { items, unread } = feed

  function open(next: boolean) {
    if (!next || unread === 0) {
      return
    }

    setFeed((current) => current && { ...current, unread: 0 })
    apiFetch("/notifications/me/seen", { method: "POST" }).catch(() => {})
  }

  return (
    <DropdownMenu onOpenChange={open}>
      <DropdownMenuTrigger
        render={
          <Button
            variant="ghost"
            size="icon"
            className="relative rounded-full"
            aria-label={
              unread > 0 ? t("unread", { count: unread }) : t("title")
            }
          />
        }
      >
        <BellIcon
          className={cn(
            "size-5 origin-top",
            unread > 0 && "animate-[bell-ring_4s_ease-in-out_infinite]"
          )}
        />
        {unread > 0 && (
          <span className="absolute -end-0.5 -top-0.5 flex h-4 min-w-4 items-center justify-center rounded-full bg-destructive px-1 text-[10px] leading-none font-medium text-white tabular-nums">
            {unread > MAX_BADGE_COUNT ? `${MAX_BADGE_COUNT}+` : unread}
          </span>
        )}
      </DropdownMenuTrigger>
      {/* At most about four notifications tall, never most of the screen; the rest scrolls,
          with a thin, quiet scrollbar. */}
      <DropdownMenuContent
        align="end"
        className="max-h-[min(26rem,70vh)] w-80 [scrollbar-width:thin] [scrollbar-color:var(--border)_transparent] p-2"
      >
        {items.length === 0 && (
          <p className="px-3 py-6 text-center text-sm text-muted-foreground">
            {t("empty")}
          </p>
        )}
        {items.map((item) => {
          const look = NOTIFICATION_LOOKS[item.kind]
          const message = text(item)

          // A kind this page doesn't know yet (a newer service) isn't shown.
          if (!look || !message) {
            return null
          }

          return (
            <DropdownMenuItem
              key={item.id}
              className="items-start gap-3 px-3 py-2.5 whitespace-normal normal-case"
              render={<Link href={item.link} />}
            >
              <look.icon
                className={cn(
                  "mt-0.5 size-4 shrink-0",
                  look.alert ? "text-destructive" : "text-primary"
                )}
              />
              <span className="min-w-0 space-y-1">
                <span className="block text-sm leading-snug">{message}</span>
                <time
                  dateTime={item.created_at}
                  className="block text-xs text-muted-foreground"
                >
                  {format.relativeTime(new Date(item.created_at), now)}
                </time>
              </span>
            </DropdownMenuItem>
          )
        })}
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
