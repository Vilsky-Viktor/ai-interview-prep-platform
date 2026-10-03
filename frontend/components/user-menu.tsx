"use client"

import { DollarSignIcon, LogOutIcon, SettingsIcon } from "lucide-react"
import Link from "next/link"
import { useTranslations } from "next-intl"

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
import { signIn, signOut } from "@/lib/auth"

export function UserMenu() {
  const t = useTranslations("userMenu")
  const signInText = useTranslations("signIn")
  const { user, loading } = useAuth()

  if (loading) {
    return <div className="size-8" />
  }

  if (!user) {
    return (
      <Button variant="outline" onClick={() => signIn(signInText("failed"))}>
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
        <Avatar size="sm">
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
          render={<Link href="/pricing" />}
        >
          <DollarSignIcon />
          {t("pricing")}
        </DropdownMenuItem>
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
          <LogOutIcon />
          {t("signOut")}
        </DropdownMenuItem>
        <DropdownMenuSeparator className="mb-3" />
        <ThemeModes />
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
