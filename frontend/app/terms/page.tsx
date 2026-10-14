import { LegalPage } from "@/components/legal-page"
import { pageMetadata } from "@/lib/site"

export const generateMetadata = () =>
  pageMetadata(
    "Terms of service",
    "The terms for using prepza: accounts, companies, credits and payments, tests for candidates, acceptable use and liability.",
    "/terms"
  )

export default async function TermsPage({
  searchParams,
}: {
  searchParams: Promise<{ version?: string }>
}) {
  const { version } = await searchParams

  return <LegalPage title="Terms" name="terms" version={version} />
}
