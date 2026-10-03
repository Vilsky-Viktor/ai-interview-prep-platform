import { translatedTitle } from "@/lib/site"
import { AdminInvite } from "@/components/company/admin-invite"

export const generateMetadata = () => translatedTitle("members", "inviteTitle")

export default async function JoinPage({
  params,
}: {
  params: Promise<{ token: string }>
}) {
  const { token } = await params

  return (
    <main className="mx-auto flex w-full max-w-5xl flex-1 flex-col items-center justify-center px-6 py-12">
      <AdminInvite token={token} />
    </main>
  )
}
