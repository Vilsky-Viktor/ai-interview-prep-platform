import { cn } from "cn"

/** One landing section: its title and text beside an illustration, which alternates sides on
 * wide screens and goes under the text on phones. */
export function LandingSection({
  title,
  text,
  reverse = false,
  children,
  extra,
}: {
  title: string
  text: string
  reverse?: boolean
  children: React.ReactNode
  extra?: React.ReactNode
}) {
  return (
    <section className="grid items-center gap-10 md:grid-cols-2 md:gap-16">
      <div className={cn("space-y-4", reverse && "md:order-last")}>
        <h2 className="font-heading text-3xl font-medium tracking-tight text-balance">
          {title}
        </h2>
        <p className="text-base leading-relaxed text-muted-foreground">
          {text}
        </p>
        {extra}
      </div>
      {children}
    </section>
  )
}

/** A still picture of the product, built from the interface's own look; screen readers skip it. */
export function Mockup({
  className,
  children,
}: {
  className?: string
  children: React.ReactNode
}) {
  return (
    <div
      aria-hidden
      className={cn(
        "space-y-3 rounded-3xl bg-card p-5 shadow-sm ring-1 ring-foreground/5",
        className
      )}
    >
      {children}
    </div>
  )
}
