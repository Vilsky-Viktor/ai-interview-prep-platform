import { cn } from "@/lib/utils"

export function Wordmark({ className }: { className?: string }) {
  return (
    <span className={cn("font-heading font-semibold tracking-tight", className)}>
      prepza<span className="text-primary">.</span>
    </span>
  )
}
