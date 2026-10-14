import { cn } from "cn"

import { MenuPill } from "@/components/menu-pill"

/** The site's select, with an optional label above it: the pill opens the site's menu, never
 * the browser's own list. */
export function PillSelect({
  label,
  ariaLabel,
  value,
  options,
  onChange,
  disabled,
  className,
  pillClassName,
}: {
  // Shown above the select; without it, `ariaLabel` names it.
  label?: string
  ariaLabel?: string
  value: string
  options: { value: string; label: string; fontFamily?: string }[]
  onChange: (value: string) => void
  disabled?: boolean
  className?: string
  // The pill's own classes: a width that stays as the choice changes, say.
  pillClassName?: string
}) {
  return (
    <div className={cn("space-y-2", className)}>
      {label && (
        <span className="block text-sm text-muted-foreground">{label}</span>
      )}
      <MenuPill
        ariaLabel={label ?? ariaLabel ?? ""}
        value={value}
        options={options.map((option) => ({ ...option, keepCase: true }))}
        onChange={onChange}
        disabled={disabled}
        className={pillClassName}
      />
    </div>
  )
}
