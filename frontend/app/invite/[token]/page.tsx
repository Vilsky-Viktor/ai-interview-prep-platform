import { translatedTitle } from "@/lib/site"
import { InviteView } from "@/components/company/invite-view"
import { PausedNotice } from "@/components/paused-notice"
import { isPaused } from "@/lib/pause"

export const generateMetadata = () => translatedTitle("invite", "title")

export default async function InvitePage({
  params,
}: {
  params: Promise<{ token: string }>
}) {
  const { token } = await params

  return (
    <main className="mx-auto flex w-full max-w-5xl flex-1 flex-col items-center justify-center px-6 py-12">
      <PausedNotice paused={await isPaused()} className="mb-10 w-full" />
      <InviteView token={token} />
    </main>
  )
}
