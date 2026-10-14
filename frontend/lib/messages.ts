import { ADMIN_MESSAGES, SERVER_ONLY_MESSAGES } from "@/constants/i18n"

type Messages = Record<string, unknown>

/** The messages client components may need: never the server-only groups, and the admin
 * zone's only `withAdmin`. */
export function clientMessages(messages: Messages, withAdmin = false) {
  const left: readonly string[] = withAdmin
    ? SERVER_ONLY_MESSAGES
    : [...SERVER_ONLY_MESSAGES, ...ADMIN_MESSAGES]

  return Object.fromEntries(
    Object.entries(messages).filter(([group]) => !left.includes(group))
  )
}
