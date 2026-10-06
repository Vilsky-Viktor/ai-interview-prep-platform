import { cn } from "cn"
import { ChevronDownIcon } from "lucide-react"

/** The site's select: a grey pill with a chevron at its end, as on the automatic top-up and
 * the question report forms. */
export function PillSelect({
  label,
  ariaLabel,
  value,
  options,
  onChange,
  disabled,
  className,
}: {
  // Shown above the select; without it, `ariaLabel` names it.
  label?: string
  ariaLabel?: string
  value: string
  options: { value: string; label: string }[]
  onChange: (value: string) => void
  disabled?: boolean
  className?: string
}) {
  return (
    <label className={cn("block space-y-2", className)}>
      {label && <span className="text-sm text-muted-foreground">{label}</span>}
      <span className="relative block rounded-full border border-transparent transition-colors focus-within:border-ring">
        <select
          value={value}
          aria-label={label ? undefined : ariaLabel}
          disabled={disabled}
          onChange={(event) => onChange(event.target.value)}
          className="h-14 w-full appearance-none rounded-full border-0 bg-muted px-6 pe-16 text-lg outline-none disabled:opacity-50 dark:bg-input/30"
        >
          {options.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
        <ChevronDownIcon
          aria-hidden
          className="pointer-events-none absolute end-6 top-1/2 size-6 -translate-y-1/2 text-muted-foreground"
        />
      </span>
    </label>
  )
}
