import type { Metadata } from "next"
import { headers } from "next/headers"
import { NextIntlClientProvider } from "next-intl"
import { getLocale, getTranslations } from "next-intl/server"

import "./globals.css"
import { AuthProvider } from "@/components/auth-provider"
import { UrlLocaleProvider } from "@/components/localized-link"
import { MaintenanceNotice } from "@/components/maintenance-notice"
import { SignInProvider } from "@/components/sign-in-dialog"
import { SiteFooter } from "@/components/site-footer"
import { SiteHeader } from "@/components/site-header"
import { ThemeProvider } from "@/components/theme-provider"
import { TooltipProvider } from "@/components/ui/tooltip"
import { Toaster } from "@/components/ui/sonner"
import { FONT_VARIABLES } from "@/constants/fonts"
import { RTL_LOCALES, type Locale } from "@/constants/i18n"
import { SITE_NAME } from "@/constants/seo"
import { previewImage, siteUrl, urlLocale } from "@/lib/site"
import { cn } from "cn"

export async function generateMetadata(): Promise<Metadata> {
  const t = await getTranslations("site")

  return {
    // Absolute links for shared pages' previews and canonical addresses.
    metadataBase: new URL(siteUrl()),
    title: { default: SITE_NAME, template: `%s · ${SITE_NAME}` },
    description: t("description"),
    openGraph: { siteName: SITE_NAME, type: "website", images: previewImage() },
    twitter: { card: "summary_large_image" },
    // Ownership checks for Google Search Console and Bing Webmaster Tools, when set.
    verification: {
      google: process.env.GOOGLE_SITE_VERIFICATION || undefined,
      other: process.env.BING_SITE_VERIFICATION
        ? { "msvalidate.01": process.env.BING_SITE_VERIFICATION }
        : undefined,
    },
  }
}

export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  // The Content-Security-Policy's nonce from proxy.ts, for the theme's inline script.
  const nonce = (await headers()).get("x-nonce") ?? undefined
  const locale = await getLocale()
  const direction = RTL_LOCALES.includes(locale as Locale) ? "rtl" : "ltr"

  return (
    // In-page links ("how it works" on the home page) scroll smoothly; Next.js turns it off for
    // navigation between pages (data-scroll-behavior), and reduced motion keeps the jump.
    <html
      lang={locale}
      dir={direction}
      data-scroll-behavior="smooth"
      suppressHydrationWarning
      className={cn(
        "scroll-smooth antialiased motion-reduce:scroll-auto",
        ...FONT_VARIABLES,
        "font-sans"
      )}
    >
      {/* A full-height column: the content grows, so the footer sits at the bottom of short
          pages without making them scroll. Pages take the full width, as auto margins in a
          flex column would otherwise shrink them to their content. */}
      <body className="flex min-h-svh flex-col">
        <NextIntlClientProvider>
          <UrlLocaleProvider locale={await urlLocale()}>
            <ThemeProvider nonce={nonce}>
              <AuthProvider>
                <TooltipProvider>
                  <SignInProvider>
                    <SiteHeader />
                    <div className="flex flex-1 flex-col [&>*]:w-full">
                      <MaintenanceNotice />
                      {children}
                    </div>
                    <SiteFooter />
                    <Toaster />
                  </SignInProvider>
                </TooltipProvider>
              </AuthProvider>
            </ThemeProvider>
          </UrlLocaleProvider>
        </NextIntlClientProvider>
      </body>
    </html>
  )
}
