import { ArrowRightIcon } from "lucide-react"
import Link from "next/link"

/** One landing section, a screen of its own: a large title and a short text, centered, and
 * its picture below. */
export function LandingSection({
  id,
  title,
  text,
  extra,
  children,
}: {
  id?: string
  title: string
  text: string
  extra?: React.ReactNode
  children?: React.ReactNode
}) {
  return (
    <section
      id={id}
      className="flex min-h-[calc(100svh-3.5rem)] scroll-mt-14 flex-col justify-center gap-8 py-12"
    >
      <div className="mx-auto max-w-2xl space-y-4 text-center">
        <h2 className="font-heading text-4xl font-medium tracking-tight text-balance sm:text-5xl">
          {title}
        </h2>
        <p className="text-lg leading-relaxed text-balance text-muted-foreground sm:text-xl">
          {text}
        </p>
        {extra}
      </div>
      {children}
    </section>
  )
}

/** The soft panel a section's picture sits on; screen readers skip the picture. */
export function Stage({ children }: { children: React.ReactNode }) {
  return (
    <div
      aria-hidden
      className="flex justify-center rounded-[2rem] bg-muted/60 px-5 py-8 sm:px-12 dark:bg-muted/30"
    >
      <div className="w-full max-w-lg">{children}</div>
    </div>
  )
}

/** A piece of interface inside a stage: plain, with a hairline edge. */
export const PANEL = "rounded-2xl border border-border/70 bg-background"

/** A quiet link onwards from a section, its arrow facing the reading direction. */
export function MoreLink({
  href,
  children,
}: {
  href: string
  children: React.ReactNode
}) {
  return (
    <Link
      href={href}
      className="inline-flex items-center gap-1.5 text-lg text-primary underline-offset-4 hover:underline"
    >
      {children}
      <ArrowRightIcon className="size-4 rtl:-scale-x-100" />
    </Link>
  )
}
