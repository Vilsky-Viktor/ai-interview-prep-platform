import { CheckIcon } from "lucide-react"

export function DoneBadge() {
  return (
    <span role="img" aria-label="Mastered"
      title="Mastered: every topic has a certificate" className="text-emerald-600 dark:text-emerald-400">
      <CheckIcon className="size-5" />
    </span>
  )
}
