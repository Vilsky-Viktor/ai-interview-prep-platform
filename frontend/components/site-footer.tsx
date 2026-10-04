import Link from "next/link"
import { getTranslations } from "next-intl/server"

export async function SiteFooter() {
  const t = await getTranslations("nav")

  return (
    <footer className="border-t">
      <div className="mx-auto flex max-w-5xl flex-wrap items-center justify-between gap-4 px-6 py-6 text-sm text-muted-foreground">
        <span>© {new Date().getFullYear()} prepza</span>
        <nav aria-label={t("legal")} className="flex flex-wrap gap-x-6 gap-y-2">
          <Link href="/pricing" className="hover:text-foreground">
            {t("pricing")}
          </Link>
          <Link href="/privacy" className="hover:text-foreground">
            {t("privacy")}
          </Link>
          <Link href="/terms" className="hover:text-foreground">
            {t("terms")}
          </Link>
          <Link href="/faq" className="hover:text-foreground">
            {t("faq")}
          </Link>
          <Link href="/about" className="hover:text-foreground">
            {t("about")}
          </Link>
          <Link href="/contact" className="hover:text-foreground">
            {t("contact")}
          </Link>
        </nav>
      </div>
    </footer>
  )
}
