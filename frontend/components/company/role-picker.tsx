"use client"

import { cn } from "cn"
import { ChevronDownIcon } from "lucide-react"
import { useTranslations } from "next-intl"

import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuRadioGroup,
  DropdownMenuRadioItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { MEMBER_ROLES, type MemberRole } from "@/constants/roles"

/** A member's role, admin or viewer: the site's select pill (components/pill-select.tsx) that
 * opens a menu with a line on what each role allows. */
export function RolePicker({
  role,
  onChange,
  disabled,
  className,
}: {
  role: MemberRole
  onChange: (role: MemberRole) => void
  disabled?: boolean
  className?: string
}) {
  const t = useTranslations("roles")
  const members = useTranslations("members")

  return (
    <DropdownMenu>
      <DropdownMenuTrigger
        disabled={disabled}
        aria-label={members("role")}
        className={cn(
          "relative flex h-14 w-full items-center rounded-full border border-transparent bg-muted px-6 pe-16 text-start text-lg transition-colors outline-none focus-visible:border-ring disabled:opacity-50 dark:bg-input/30",
          className
        )}
      >
        {t(role)}
        <ChevronDownIcon
          aria-hidden
          className="pointer-events-none absolute end-6 top-1/2 size-6 -translate-y-1/2 text-muted-foreground"
        />
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-72 p-2">
        <DropdownMenuRadioGroup
          value={role}
          onValueChange={(value) => onChange(value as MemberRole)}
        >
          {MEMBER_ROLES.map((option) => (
            <DropdownMenuRadioItem
              key={option}
              value={option}
              className="items-start px-3 py-2"
            >
              <span className="space-y-0.5">
                <span className="block">{t(option)}</span>
                <span className="block text-sm text-muted-foreground">
                  {t(`${option}Note`)}
                </span>
              </span>
            </DropdownMenuRadioItem>
          ))}
        </DropdownMenuRadioGroup>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
