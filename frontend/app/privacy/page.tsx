import { notFound } from "next/navigation"

import { LegalPage } from "@/components/legal-page"
import { publicFetch } from "@/lib/server-api"
import { pageMetadata } from "@/lib/site"
import type { LegalDocument } from "@/types/help"

export const generateMetadata = () =>
  pageMetadata(
    "Privacy policy",
    "How prepza collects, uses and protects the personal data of companies, their members and candidates, and the rights you have.",
    "/privacy"
  )

export default async function PrivacyPage() {
  const document = await publicFetch<LegalDocument>(
    "/rounds/help/legal/privacy"
  )

  if (!document) {
    notFound()
  }

  return <LegalPage title="Privacy" document={document} />
}
