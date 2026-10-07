import { notFound } from "next/navigation"

import { LegalPage } from "@/components/legal-page"
import { serverFetch } from "@/lib/server-api"
import { pageMetadata } from "@/lib/site"
import type { LegalDocument } from "@/types/help"

export const generateMetadata = () =>
  pageMetadata(
    "Data processing agreement",
    "The data processing agreement between prepza and companies that test candidates: what prepza processes on your behalf and how.",
    "/dpa"
  )

export default async function DpaPage() {
  const document = await serverFetch<LegalDocument>("/rounds/help/legal/dpa")

  if (!document) {
    notFound()
  }

  return <LegalPage title="Data processing agreement" document={document} />
}
