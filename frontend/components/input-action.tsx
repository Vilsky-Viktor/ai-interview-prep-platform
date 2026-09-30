import type { ComponentProps, ReactNode } from "react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"

export function InputAction({
  action,
  disabled,
  icon,
  ...props
}: ComponentProps<typeof Input> & {
  action: string
  disabled?: boolean
  icon?: ReactNode
}) {
  return (
    <div
      className={
        icon
          ? "relative min-w-0 flex-1 rounded-lg border border-transparent transition-colors focus-within:border-ring"
          : "relative min-w-0 flex-1"
      }
    >
      <Input
        className={
          icon
            ? "h-16 border-0 px-6 pr-20 text-lg focus-visible:ring-0 md:text-lg"
            : "h-12 px-4 pr-32"
        }
        {...props}
      />
      <Button
        type="submit"
        disabled={disabled}
        size={icon ? "icon" : "default"}
        className={
          icon
            ? "absolute top-3 right-3 size-10 rounded-full"
            : "absolute top-2 right-2"
        }
        aria-label={icon ? action : undefined}
      >
        {icon ?? action}
      </Button>
    </div>
  )
}
