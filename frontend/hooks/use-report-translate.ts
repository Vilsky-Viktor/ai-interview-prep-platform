import { useTranslations } from "next-intl"

/** The texts a report's chat summary is written in: the integrity signals' from the candidates'
 * messages, the rest from the report's. */
export function useReportTranslate() {
  const t = useTranslations("report")
  const candidates = useTranslations("candidates")

  return (key: string, values?: Record<string, string | number>) =>
    ["pageLeaves", "copies", "fastAnswers"].includes(key)
      ? candidates(key, values)
      : t(key, values)
}
