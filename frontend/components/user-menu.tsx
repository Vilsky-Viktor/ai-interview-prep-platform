"use client"

import { LogOutIcon } from "lucide-react"

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
  const { user, loading } = useAuth()

  if (loading) {
    return <div className="size-8" />
  }

  if (!user) {
    return (
      <Button variant="outline" onClick={() => signIn()}>
        Sign in
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
            aria-label="Account"
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
          variant="destructive"
          onClick={() => signOut()}
        >
          <LogOutIcon />
          Sign out
        </DropdownMenuItem>
        <DropdownMenuSeparator className="mb-3" />
        <ThemeModes />
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
