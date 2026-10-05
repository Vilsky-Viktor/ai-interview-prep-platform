import { cn } from "cn"
import Link from "next/link"

/** A page's slim tabs under its title: the current one over a blue line. */
export function TabNav({
  items,
  current,
}: {
  items: readonly { id: string; href: string; label: string }[]
  current: string
}) {
  return (
    <nav className="flex gap-8 border-b">
      {items.map((item) => (
        <Link
          key={item.id}
          href={item.href}
          aria-current={item.id === current ? "page" : undefined}
          className={cn(
            "-mb-px border-b-2 pb-3 text-base lowercase transition-colors",
            item.id === current
              ? "border-primary text-foreground"
              : "border-transparent text-muted-foreground hover:text-foreground"
          )}
        >
          {item.label}
        </Link>
      ))}
    </nav>
  )
}
