import type { Metadata } from "next"

import { LegalPage } from "@/components/legal-page"
import { TERMS_INTRO, TERMS_SECTIONS } from "@/constants/terms"

export const metadata: Metadata = { title: "Terms" }

export default function TermsPage() {
  return (
    <LegalPage title="Terms" intro={TERMS_INTRO} sections={TERMS_SECTIONS} />
  )
}
