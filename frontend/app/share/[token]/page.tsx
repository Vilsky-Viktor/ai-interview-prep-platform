import { translatedTitle } from "@/lib/site"
import { ShareInvite } from "@/components/preparations/share-invite"

export const generateMetadata = () => translatedTitle("share", "inviteTitle")

export default async function SharePage({
  params,
}: {
  params: Promise<{ token: string }>
}) {
  const { token } = await params

  return (
    <main className="mx-auto flex w-full max-w-5xl flex-1 flex-col items-center justify-center px-6 py-12">
      <ShareInvite token={token} />
    </main>
  )
}
