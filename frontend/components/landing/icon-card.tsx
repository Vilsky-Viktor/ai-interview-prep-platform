import { cn } from "cn"
import type { LucideIcon } from "lucide-react"

import { KeepAcronyms } from "@/components/keep-acronyms"

/** A grey landing card: a title ending with the logo's blue dot, a short line and its icon in
 * the top corner; ringed while `lit`. */
export function IconCard({
  icon: Icon,
  title,
  lit = false,
  children,
}: {
  icon: LucideIcon
  title: string
  lit?: boolean
  children: React.ReactNode
}) {
  return (
    <li
      data-lit={lit || undefined}
      className={cn(
        "relative flex flex-col justify-center gap-1.5 rounded-2xl bg-muted p-4 pe-14 transition-shadow duration-300 sm:p-5 sm:pe-16 dark:bg-card",
        lit && "ring-2 ring-primary"
      )}
    >
      <Icon className="absolute end-4 top-4 size-8 text-primary sm:end-5 sm:top-5" />
      <span className="font-heading text-xl font-medium lowercase">
        <KeepAcronyms text={title} />
        <span className="text-primary">.</span>
      </span>
      <span className="text-sm leading-snug text-muted-foreground">
        {children}
      </span>
    </li>
  )
}
