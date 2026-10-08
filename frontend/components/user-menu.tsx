"use client"

import {
  DollarSignIcon,
  ShieldCogCornerIcon,
  LogOutIcon,
  SettingsIcon,
} from "lucide-react"
import Link from "next/link"
import { useTranslations } from "next-intl"
import { useEffect, useState } from "react"

import { useSignIn } from "@/components/sign-in-dialog"
import { useAuth } from "@/components/auth-provider"
import { ThemeModes } from "@/components/theme-toggle"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { apiFetch } from "@/lib/api"
import { signOut } from "@/lib/auth"

export function UserMenu() {
  const t = useTranslations("userMenu")
  const signIn = useSignIn()
  const { user, loading } = useAuth()
  // The backend says whether this account may open the superadmin pages; kept by account, so a
  // different sign-in never inherits it.
  const [superadminUid, setSuperadminUid] = useState<string | null>(null)
  const superadmin = user !== null && superadminUid === user.uid

  useEffect(() => {
    if (!user) {
      return
    }

    apiFetch<{ is_superadmin: boolean }>("/library/me")
      .then((me) => setSuperadminUid(me.is_superadmin ? user.uid : null))
      .catch(() => setSuperadminUid(null))
  }, [user])

  if (loading) {
    return <div className="size-8" />
  }

  if (!user) {
    return (
      <Button variant="outline" className="px-4" onClick={() => signIn()}>
        {t("signIn")}
      </Button>
    )
  }

  const initial = (user.displayName ?? user.email ?? "?")[0].toUpperCase()

  return (
    <DropdownMenu>
      <DropdownMenuTrigger
        render={
          <Button
            variant="ghost"
            size="icon"
            className="rounded-full"
            aria-label={t("account")}
          />
        }
      >
        <Avatar size="sm" className="data-[size=sm]:size-7">
          <AvatarImage src={user.photoURL ?? undefined} alt="" />
          <AvatarFallback>{initial}</AvatarFallback>
        </Avatar>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-56 p-2">
        <DropdownMenuGroup>
          <DropdownMenuLabel className="px-3 py-2">
            <p className="truncate text-sm text-foreground">
              {user.displayName}
            </p>
            <p className="truncate font-normal">{user.email}</p>
          </DropdownMenuLabel>
        </DropdownMenuGroup>
        <DropdownMenuSeparator />
        <DropdownMenuItem
          className="px-3 py-2"
          render={<Link href="/top-up" />}
        >
          <DollarSignIcon />
          {t("topUp")}
        </DropdownMenuItem>
        {superadmin && (
          <DropdownMenuItem
            className="px-3 py-2"
            render={<Link href="/superadmin/templates" />}
          >
            <ShieldCogCornerIcon />
            {t("adminZone")}
          </DropdownMenuItem>
        )}
        <DropdownMenuItem
          className="px-3 py-2"
          render={<Link href="/settings" />}
        >
          <SettingsIcon />
          {t("settings")}
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem
          className="px-3 py-2"
          variant="destructive"
          onClick={() => signOut()}
        >
          <LogOutIcon className="rtl:-scale-x-100" />
          {t("signOut")}
        </DropdownMenuItem>
        <DropdownMenuSeparator className="mb-3" />
        <ThemeModes />
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
