import { ConnectView } from "@/components/connect/connect-view"
import { translatedTitle } from "@/lib/site"

export const generateMetadata = () => translatedTitle("connect", "pageTitle")

/** An AI app sends the user here to allow or deny it the use of their account
 * (`?request=` names the app's request, kept by the API for a few minutes). */
export default async function ConnectPage({
  searchParams,
}: {
  searchParams: Promise<{ request?: string }>
}) {
  const { request } = await searchParams

  return (
    <main className="mx-auto flex w-full max-w-5xl flex-1 flex-col items-center justify-center px-6 py-12">
      <ConnectView requestId={request ?? ""} />
    </main>
  )
}
