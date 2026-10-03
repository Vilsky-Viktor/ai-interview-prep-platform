import type { Metadata } from "next"
import { notFound } from "next/navigation"

import { LegalPage } from "@/components/legal-page"
import { serverFetch } from "@/lib/server-api"
import type { LegalDocument } from "@/types/help"

export const metadata: Metadata = { title: "Terms" }

export default async function TermsPage() {
  const document = await serverFetch<LegalDocument>("/rounds/help/legal/terms")

  if (!document) {
    notFound()
  }

  return <LegalPage title="Terms" document={document} />
}
