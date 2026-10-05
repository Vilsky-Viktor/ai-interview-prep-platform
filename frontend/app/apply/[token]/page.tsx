import { LinkView } from "@/components/company/link-view"
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
      <LinkView token={token} />
    </main>
  )
}
