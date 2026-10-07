"use client"

import { useTranslations } from "next-intl"

import { MenuPill } from "@/components/menu-pill"
import { MEMBER_ROLES, type MemberRole } from "@/constants/roles"

/** A member's role, admin or viewer: the site's select pill opening a menu with a line on what
 * each role allows. */
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
    <MenuPill
      ariaLabel={members("role")}
      value={role}
      options={MEMBER_ROLES.map((option) => ({
        value: option,
        label: t(option),
        note: t(`${option}Note`),
      }))}
      onChange={(value) => onChange(value as MemberRole)}
      disabled={disabled}
      className={className}
    />
  )
}
