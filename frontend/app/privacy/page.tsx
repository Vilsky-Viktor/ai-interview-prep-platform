import type { Metadata } from "next"

import { LegalPage } from "@/components/legal-page"
import { PRIVACY_INTRO, PRIVACY_SECTIONS } from "@/constants/privacy"

export const metadata: Metadata = { title: "Privacy policy" }

export default function PrivacyPage() {
  return (
    <LegalPage
      title="Privacy policy"
      intro={PRIVACY_INTRO}
      sections={PRIVACY_SECTIONS}
    />
  )
}
