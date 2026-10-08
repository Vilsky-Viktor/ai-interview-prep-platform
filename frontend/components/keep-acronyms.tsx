/** A title's text with its acronyms (ATS, PDF) and Slack's name as written, though titles are
 * lowercase. */
export function KeepAcronyms({ text }: { text: string }) {
  return text.split(/\b([A-Z]{2,}|Slack)\b/).map((part, index) =>
    index % 2 ? (
      <span key={index} className="normal-case">
        {part}
      </span>
    ) : (
      part
    )
  )
}
