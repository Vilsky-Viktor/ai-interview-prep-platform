import { cn } from "cn"

/** One landing section: a large title and a short text, then its picture below. */
export function LandingSection({
  title,
  text,
  extra,
  children,
}: {
  title: string
  text: string
  extra?: React.ReactNode
  children?: React.ReactNode
}) {
  return (
    <section className="space-y-10">
      <div className="max-w-2xl space-y-4">
        <h2 className="font-heading text-3xl font-medium tracking-tight text-balance sm:text-4xl">
          {title}
        </h2>
        <p className="text-lg leading-relaxed text-pretty text-muted-foreground">
          {text}
        </p>
        {extra}
      </div>
      {children}
    </section>
  )
}

/** The soft panel a section's picture sits on; screen readers skip the picture. */
export function Stage({
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
        "flex justify-center rounded-[2rem] bg-muted/60 px-5 py-10 sm:px-12 sm:py-14 dark:bg-muted/30",
        className
      )}
    >
      <div className="w-full max-w-md">{children}</div>
    </div>
  )
}

/** A piece of interface inside a stage: plain, with a hairline edge. */
export const PANEL =
  "rounded-2xl border border-border/70 bg-background text-sm"
