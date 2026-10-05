import { cn } from "cn"
import type { ComponentProps, ReactNode } from "react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"

export function InputAction({
  action,
  disabled,
  icon,
  addon,
  ...props
}: ComponentProps<typeof Input> & {
  action: string
  disabled?: boolean
  icon?: ReactNode
  // Controls inside the field, before its button (a search's filters).
  addon?: ReactNode
}) {
  if (addon) {
    return (
      // On phones the text takes its own row and the controls the row under it, inside the same
      // field; from sm up it's one rounded row.
      <div className="flex min-w-0 flex-1 flex-wrap items-center gap-2 rounded-[2rem] border border-transparent bg-muted pe-3 pb-3 transition-colors focus-within:border-ring sm:flex-nowrap sm:rounded-full sm:pb-0 dark:bg-input/30">
        <Input
          className="h-16 min-w-0 flex-1 basis-full border-0 bg-transparent px-6 text-lg focus-visible:ring-0 sm:basis-auto md:text-lg dark:bg-transparent"
          {...props}
        />
        {addon}
        <Button
          type="submit"
          disabled={disabled}
          size="icon"
          className="ms-auto size-10 shrink-0 rounded-full sm:ms-0"
          aria-label={action}
        >
          {icon ?? action}
        </Button>
      </div>
    )
  }

  // The site's big borderless field; an icon button, or a text one (e.g. "share & start").
  return (
    <div className="relative min-w-0 flex-1 rounded-full border border-transparent transition-colors focus-within:border-ring">
      <Input
        className={cn(
          "h-16 border-0 px-6 text-lg focus-visible:ring-0 md:text-lg",
          icon ? "pe-20" : "pe-48"
        )}
        {...props}
      />
      <Button
        type="submit"
        disabled={disabled}
        size={icon ? "icon" : "default"}
        className={
          icon
            ? "absolute end-3 top-3 size-10 rounded-full"
            : "absolute end-3 top-3 h-10 px-5 text-base"
        }
        aria-label={icon ? action : undefined}
      >
        {icon ?? action}
      </Button>
    </div>
  )
}
