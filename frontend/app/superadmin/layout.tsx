import { NextIntlClientProvider } from "next-intl"
import { getMessages } from "next-intl/server"

import { clientMessages } from "@/lib/messages"

/** The admin zone's pages get its texts too; every other page's browser leaves them out. */
export default async function SuperadminLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <NextIntlClientProvider
      messages={clientMessages(await getMessages(), true)}
    >
      {children}
    </NextIntlClientProvider>
  )
}
