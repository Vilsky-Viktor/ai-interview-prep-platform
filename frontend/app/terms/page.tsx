import { notFound } from "next/navigation"

import { LegalPage } from "@/components/legal-page"
import { serverFetch } from "@/lib/server-api"
import { pageMetadata } from "@/lib/site"
import type { LegalDocument } from "@/types/help"

export const generateMetadata = () =>
  pageMetadata(
    "Terms of service",
    "The terms for using prepza: accounts, companies, credits and payments, tests for candidates, acceptable use and liability.",
    "/terms"
  )

export default async function TermsPage() {
  const document = await serverFetch<LegalDocument>("/rounds/help/legal/terms")

  if (!document) {
    notFound()
  }

  return <LegalPage title="Terms" document={document} />
}
