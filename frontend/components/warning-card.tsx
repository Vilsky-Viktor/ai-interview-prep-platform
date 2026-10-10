import { cn } from "cn"
import { InfoIcon, TriangleAlertIcon } from "lucide-react"

type CardProps = { children: React.ReactNode; className?: string }

/** A notice on a gray card: a large sign and the text in the muted color, as the maintenance
 * notice shows it. */
function NoticeCard({
  children,
  className,
  icon,
}: CardProps & { icon: React.ReactNode }) {
  return (
    <div
      role="status"
      className={cn(
        "flex items-center gap-4 rounded-2xl bg-muted p-5 text-base",
        className
      )}
    >
      {icon}
      <p className="text-muted-foreground">{children}</p>
    </div>
  )
}

/** A warning: an amber warning sign. */
export function WarningCard(props: CardProps) {
  return (
    <NoticeCard
      {...props}
      icon={
        <TriangleAlertIcon
          aria-hidden
          className="size-7 shrink-0 text-amber-600 dark:text-amber-400"
        />
      }
    />
  )
}

/** Information: a sign in the primary color. */
export function InfoCard(props: CardProps) {
  return (
    <NoticeCard
      {...props}
      icon={<InfoIcon aria-hidden className="size-7 shrink-0 text-primary" />}
    />
  )
}
