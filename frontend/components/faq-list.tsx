import { ChevronDownIcon } from "lucide-react"

import type { FaqItem } from "@/types/help"

/** Questions that open to their answers, as on the FAQ page. */
export function FaqList({ items }: { items: FaqItem[] }) {
  return (
    <div className="divide-y rounded-3xl bg-card shadow-sm ring-1 ring-foreground/5">
      {items.map((item) => (
        <details key={item.key} className="group px-6">
          <summary className="flex cursor-pointer list-none items-center justify-between gap-4 py-5 font-medium [&::-webkit-details-marker]:hidden">
            {item.question}
            <ChevronDownIcon className="size-5 shrink-0 text-muted-foreground transition-transform group-open:rotate-180" />
          </summary>
          <p className="pb-5 text-base leading-relaxed text-muted-foreground">
            {item.answer}
          </p>
        </details>
      ))}
    </div>
  )
}
