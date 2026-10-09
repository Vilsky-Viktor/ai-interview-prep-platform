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
      <div className="mx-auto flex max-w-5xl flex-wrap justify-between gap-8 px-6 py-8 text-sm text-muted-foreground">
        <div className="space-y-6">
          <span className="block">
            © {new Date().getFullYear()} prepza
            <span className="text-primary">.</span>
          </span>
          {/* prepza's social accounts; links come once the accounts exist. */}
          <div className="flex items-center gap-5">
            <span role="img" aria-label="LinkedIn">
              <LinkedInIcon className="size-6" />
            </span>
            <span role="img" aria-label="X">
              <XIcon className="size-6" />
            </span>
            <span role="img" aria-label="YouTube">
              <YouTubeIcon className="size-6" />
            </span>
            <span role="img" aria-label="Facebook">
              <FacebookIcon className="size-6" />
            </span>
          </div>
          <AskAgentButton className="h-10 px-5 text-sm" />
        </div>
        {/* Lowercase with the blue dot, like the header's menu (globals.css, by data-slot). */}
        <nav
          data-slot="footer-nav"
          aria-label={t("footer")}
          className="grid grid-cols-3 gap-x-6 sm:gap-x-16"
        >
          {FOOTER_COLUMNS.map((column) => (
            <ul key={column[0].href} className="space-y-2">
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
