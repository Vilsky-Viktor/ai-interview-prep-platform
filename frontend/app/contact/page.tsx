import { getTranslations } from "next-intl/server"

import { ContactForm } from "@/components/contact-form"
import { pageMetadata } from "@/lib/site"

export async function generateMetadata() {
  const t = await getTranslations("contact")

  return pageMetadata(t("title"), t("description"), "/contact", true)
}

export default async function ContactPage() {
  const t = await getTranslations("contact")

  return (
    <main className="mx-auto max-w-5xl space-y-10 px-6 py-12">
      <header className="space-y-4">
        <h1 className="font-heading text-4xl font-medium tracking-tight">
          {t("title")}
        </h1>
        <p className="text-base text-muted-foreground">{t("intro")}</p>
      </header>
      <ContactForm />
    </main>
  )
}
