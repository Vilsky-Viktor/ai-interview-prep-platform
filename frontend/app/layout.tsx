import type { Metadata } from "next"
import { Geist, Geist_Mono, Poppins } from "next/font/google"
import { headers } from "next/headers"

import "./globals.css"
import { AuthProvider } from "@/components/auth-provider"
import { SiteFooter } from "@/components/site-footer"
import { SiteHeader } from "@/components/site-header"
import { ThemeProvider } from "@/components/theme-provider"
import { Toaster } from "@/components/ui/sonner"
import { cn } from "@/lib/utils"

const geist = Geist({ subsets: ["latin"], variable: "--font-geist" })

const geistMono = Geist_Mono({ subsets: ["latin"], variable: "--font-mono" })

const poppins = Poppins({
  subsets: ["latin"],
  weight: ["500", "600"],
  variable: "--font-poppins",
})

export const metadata: Metadata = {
  title: { default: "prepza.", template: "%s · prepza." },
  description:
    "Prepare for interviews with AI-generated multiple-choice questions, practice rounds and certificates.",
}

export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  // The Content-Security-Policy's nonce from proxy.ts, for the theme's inline script.
  const nonce = (await headers()).get("x-nonce") ?? undefined

  return (
    <html
      lang="en"
      suppressHydrationWarning
      className={cn(
        "antialiased",
        geist.variable,
        geistMono.variable,
        poppins.variable,
        "font-sans"
      )}
    >
      <body>
        <ThemeProvider nonce={nonce}>
          <AuthProvider>
            <SiteHeader />
            {children}
            <SiteFooter />
            <Toaster />
          </AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  )
}
