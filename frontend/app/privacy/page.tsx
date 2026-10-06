import type { Metadata } from "next"
import { notFound } from "next/navigation"

import { LegalPage } from "@/components/legal-page"
import { serverFetch } from "@/lib/server-api"
import type { LegalDocument } from "@/types/help"

export const metadata: Metadata = { title: "Privacy" }

export default async function PrivacyPage() {
  const document = await serverFetch<LegalDocument>(
    "/rounds/help/legal/privacy"
  )

  if (!document) {
    notFound()
  }

  return <LegalPage title="Privacy" document={document} />
}
