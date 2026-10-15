import { LinkView } from "@/components/company/link-view"
import { PausedNotice } from "@/components/paused-notice"
import { isPaused } from "@/lib/pause"
import { translatedTitle } from "@/lib/site"

export const generateMetadata = () => translatedTitle("invite", "title")

/** A test's shareable link, as a company puts it in a job ad; laid out like an invite. */
export default async function ApplyPage({
  params,
}: {
  params: Promise<{ token: string }>
}) {
  const { token } = await params

  return (
    <main className="mx-auto flex w-full max-w-5xl flex-1 flex-col items-center justify-center px-6 py-12">
      <PausedNotice paused={await isPaused()} className="mb-10 w-full" />
      <LinkView token={token} />
    </main>
  )
}
