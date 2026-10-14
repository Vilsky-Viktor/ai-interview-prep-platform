import { LegalPage } from "@/components/legal-page"
import { pageMetadata } from "@/lib/site"

export const generateMetadata = () =>
  pageMetadata(
    "Privacy policy",
    "How prepza collects, uses and protects the personal data of companies, their members and candidates, and the rights you have.",
    "/privacy"
  )

export default async function PrivacyPage({
  searchParams,
}: {
  searchParams: Promise<{ version?: string }>
}) {
  const { version } = await searchParams

  return <LegalPage title="Privacy" name="privacy" version={version} />
}
