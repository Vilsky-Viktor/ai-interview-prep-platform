import { SearchIcon } from "lucide-react"

import { Caret } from "@/components/landing/caret"
import { buttonVariants } from "@/components/ui/button"

/** The site's search field (components/input-action.tsx) as a small picture: `text` as typed
 * so far (the `placeholder` while null) and a caret while `typing`. */
export function TypedSearch({
  ref,
  text,
  typing,
  placeholder,
}: {
  ref?: React.Ref<HTMLDivElement>
  text: string | null
  typing: boolean
  placeholder: string
}) {
  return (
    <div
      ref={ref}
      className="flex h-11 items-center gap-2 rounded-full bg-muted ps-4 pe-1.5 dark:bg-input/30"
    >
      {/* One line's height whatever it holds, so the caret never moves the text. */}
      <span className="flex h-5 min-w-0 flex-1 items-center">
        {text === null ? (
          <span className="truncate text-muted-foreground lowercase">
            {placeholder}
          </span>
        ) : (
          <>
            <span className="truncate">{text}</span>
            {typing && <Caret />}
          </>
        )}
      </span>
      <span
        className={buttonVariants({
          size: "icon",
          className: "size-8 rounded-full",
        })}
      >
        <SearchIcon />
      </span>
    </div>
  )
}
