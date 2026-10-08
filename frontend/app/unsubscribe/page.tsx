import { translatedTitle } from "@/lib/site"
import { UnsubscribeView } from "@/components/unsubscribe-view"

export const generateMetadata = () => translatedTitle("unsubscribe", "title")

/** An email's unsubscribe link opens here, signed in or not. */
export default async function UnsubscribePage({
  searchParams,
}: {
  searchParams: Promise<{ token?: string }>
}) {
  const { token } = await searchParams

  return (
    <main className="mx-auto flex w-full max-w-5xl flex-1 flex-col items-center justify-center px-6 py-12">
      <UnsubscribeView token={token ?? ""} />
    </main>
  )
}
