import type { Metadata } from "next"
import { Geist, Geist_Mono, Poppins } from "next/font/google"
import { headers } from "next/headers"
import { NextIntlClientProvider } from "next-intl"
import { getLocale, getTranslations } from "next-intl/server"

import "./globals.css"
import { AuthProvider } from "@/components/auth-provider"
import { SiteFooter } from "@/components/site-footer"
import { SiteHeader } from "@/components/site-header"
import { ThemeProvider } from "@/components/theme-provider"
import { Toaster } from "@/components/ui/sonner"
import { SITE_NAME } from "@/constants/seo"
import { siteUrl } from "@/lib/site"
import { cn } from "cn"

const geist = Geist({ subsets: ["latin"], variable: "--font-geist" })

const geistMono = Geist_Mono({ subsets: ["latin"], variable: "--font-mono" })

const poppins = Poppins({
  subsets: ["latin"],
  weight: ["500", "600"],
  variable: "--font-poppins",
})

export async function generateMetadata(): Promise<Metadata> {
  const t = await getTranslations("site")

  return {
    // Absolute links for shared pages' previews and canonical addresses.
    metadataBase: new URL(siteUrl()),
    title: { default: SITE_NAME, template: `%s · ${SITE_NAME}` },
    description: t("description"),
    openGraph: { siteName: SITE_NAME, type: "website" },
    twitter: { card: "summary" },
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

  return (
    <html
      lang={locale}
      suppressHydrationWarning
      className={cn(
        "antialiased",
        geist.variable,
        geistMono.variable,
        poppins.variable,
        "font-sans"
      )}
    >
      {/* A full-height column: the content grows, so the footer sits at the bottom of short
          pages without making them scroll. Pages take the full width, as auto margins in a
          flex column would otherwise shrink them to their content. */}
      <body className="flex min-h-svh flex-col">
        <NextIntlClientProvider>
          <ThemeProvider nonce={nonce}>
            <AuthProvider>
              <SiteHeader />
              <div className="flex flex-1 flex-col [&>*]:w-full">
                {children}
              </div>
              <SiteFooter />
              <Toaster />
            </AuthProvider>
          </ThemeProvider>
        </NextIntlClientProvider>
      </body>
    </html>
  )
}
