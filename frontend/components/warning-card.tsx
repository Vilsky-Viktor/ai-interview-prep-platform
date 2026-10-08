import { TriangleAlertIcon } from "lucide-react"

/** A warning on a gray card: a large amber warning sign and the text in the muted color, as the
 * maintenance notice shows it. */
export function WarningCard({ children }: { children: React.ReactNode }) {
  return (
    <div
      role="status"
      className="flex items-center gap-4 rounded-2xl bg-muted p-5 text-base"
    >
      <TriangleAlertIcon
        aria-hidden
        className="size-7 shrink-0 text-amber-600 dark:text-amber-400"
      />
      <p className="text-muted-foreground">{children}</p>
    </div>
  )
}
