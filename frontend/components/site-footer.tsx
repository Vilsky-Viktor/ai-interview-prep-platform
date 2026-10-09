import { getTranslations } from "next-intl/server"

import {
  FacebookIcon,
  LinkedInIcon,
  XIcon,
  YouTubeIcon,
} from "@/components/brand-icons"
import { AskAgentButton } from "@/components/landing/ask-agent-button"
import { LocalizedLink } from "@/components/localized-link"
import { FOOTER_COLUMNS } from "@/constants/navigation"

export async function SiteFooter() {
  const t = await getTranslations("nav")

  return (
    <footer className="border-t">
      {/* On phones: everything centered in one column, with bigger icons, button and links. */}
      <div className="mx-auto flex max-w-5xl flex-wrap justify-between gap-8 px-6 py-8 text-sm text-muted-foreground max-sm:flex-col max-sm:items-center max-sm:gap-10 max-sm:py-12 max-sm:text-center">
        <div className="space-y-6 max-sm:flex max-sm:flex-col max-sm:items-center">
          <span className="block">
            © {new Date().getFullYear()} prepza
            <span className="text-primary">.</span>
          </span>
          {/* prepza's social accounts; links come once the accounts exist. */}
          <div className="flex items-center gap-5 max-sm:gap-8">
            <span role="img" aria-label="LinkedIn">
              <LinkedInIcon className="size-6 max-sm:size-8" />
            </span>
            <span role="img" aria-label="X">
              <XIcon className="size-6 max-sm:size-8" />
            </span>
            <span role="img" aria-label="YouTube">
              <YouTubeIcon className="size-6 max-sm:size-8" />
            </span>
            <span role="img" aria-label="Facebook">
              <FacebookIcon className="size-6 max-sm:size-8" />
            </span>
          </div>
          <AskAgentButton className="h-10 px-5 text-sm max-sm:h-12 max-sm:px-6 max-sm:text-base" />
        </div>
        {/* Lowercase with the blue dot, like the header's menu (globals.css, by data-slot). */}
        <nav
          data-slot="footer-nav"
          aria-label={t("footer")}
          className="grid grid-cols-3 gap-x-6 [overflow-wrap:anywhere] hyphens-auto max-sm:grid-cols-1 max-sm:gap-y-3 max-sm:text-lg sm:gap-x-16"
        >
          {FOOTER_COLUMNS.map((column) => (
            <ul key={column[0].href} className="space-y-2 max-sm:space-y-3">
              {column.map((link) => (
                <li key={link.href}>
                  <LocalizedLink
                    href={link.href}
                    className="hover:text-foreground"
                  >
                    {t(link.label)}
                  </LocalizedLink>
                </li>
              ))}
            </ul>
          ))}
        </nav>
      </div>
    </footer>
  )
}
