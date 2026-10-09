import { cn } from "cn"
import { ArrowRightIcon } from "lucide-react"

import { KeepAcronyms } from "@/components/keep-acronyms"
import { LocalizedLink } from "@/components/localized-link"
import { buttonVariants } from "@/components/ui/button"

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
      className="flex min-h-[calc(100svh-3.5rem)] scroll-mt-14 flex-col justify-center gap-8 py-20 sm:py-28"
    >
      <div className="mx-auto max-w-3xl space-y-4 text-center">
        {/* A title over two lines ends each with the logo's blue dot, like the hero's. */}
        <h2
          className={cn(
            "font-heading text-4xl font-medium tracking-tight text-balance sm:text-5xl",
            title.includes("\n") && "no-dot"
          )}
        >
          {title.includes("\n") ? (
            title.split("\n").map((line) => (
              <span key={line} className="block">
                <KeepAcronyms text={line} />
                <span className="text-primary">.</span>
              </span>
            ))
          ) : (
            <KeepAcronyms text={title} />
          )}
        </h2>
        <p className="mx-auto max-w-2xl text-lg leading-relaxed text-balance text-muted-foreground sm:text-xl">
          {text}
        </p>
        {extra}
      </div>
      {children}
    </section>
  )
}

/** The soft panel a section's picture sits on. Screen readers skip the picture unless it holds
 * real links (`decorative={false}`); `wide` gives room for two pictures side by side. On phones
 * it spans the screen, out to its edges, with square corners. */
export function Stage({
  wide = false,
  decorative = true,
  children,
}: {
  wide?: boolean
  decorative?: boolean
  children: React.ReactNode
}) {
  return (
    <div
      aria-hidden={decorative}
      className="-mx-6 flex justify-center bg-muted/60 px-5 py-10 sm:mx-0 sm:rounded-[2rem] sm:px-12 dark:bg-muted/30"
    >
      <div className={wide ? "w-full max-w-4xl" : "w-full max-w-2xl"}>
        {children}
      </div>
    </div>
  )
}

/** A piece of interface inside a stage: plain, with a hairline edge. */
export const PANEL = "rounded-2xl border border-border/70 bg-background"

/** A link onwards from a section, as an outline button; its arrow faces the reading direction. */
export function MoreLink({
  href,
  keepCase = false,
  children,
}: {
  href: string
  // For a label written in lowercase already, with an abbreviation to keep ("go to FAQ").
  keepCase?: boolean
  children: React.ReactNode
}) {
  return (
    <LocalizedLink
      href={href}
      className={cn(
        buttonVariants({ variant: "outline" }),
        "h-11 gap-2 border-foreground/20 px-6 text-base dark:border-input",
        keepCase ? "normal-case" : "lowercase"
      )}
    >
      {children}
      <ArrowRightIcon className="size-4 rtl:-scale-x-100" />
    </LocalizedLink>
  )
}
