import type { Metadata } from "next"
import { notFound } from "next/navigation"

import { LegalPage } from "@/components/legal-page"
import { serverFetch } from "@/lib/server-api"
import type { LegalDocument } from "@/types/help"

export const metadata: Metadata = { title: "Data processing agreement" }

export default async function DpaPage() {
  const document = await serverFetch<LegalDocument>("/rounds/help/legal/dpa")

  if (!document) {
    notFound()
  }

  return <LegalPage title="Data processing agreement" document={document} />
}
