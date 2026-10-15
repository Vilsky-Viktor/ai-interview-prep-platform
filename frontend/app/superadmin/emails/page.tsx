import { EmailLookupView } from "@/components/superadmin/email-lookup"
import { SuperadminHeader } from "@/components/superadmin/superadmin-header"
import { translatedTitle } from "@/lib/site"

export const generateMetadata = () => translatedTitle("superadmin", "zone")

/** The admin zone's emails tab: finds an address and stops the emails prepza sends to it, for
 * someone who asked by email. The API answers superadmins only. */
export default async function EmailsPage() {
  return (
    <main className="mx-auto max-w-5xl space-y-8 px-6 py-12">
      <SuperadminHeader current="emails" />
      <EmailLookupView />
    </main>
  )
}
