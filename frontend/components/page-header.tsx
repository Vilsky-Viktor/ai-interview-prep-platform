import type { ReactNode } from "react"

export function PageHeader({
  back,
  before,
  tags,
  title,
  children,
}: {
  back: ReactNode
  before?: ReactNode
  // Tags such as a status, just under the title.
  tags?: ReactNode
  title: ReactNode
  children?: ReactNode
}) {
  return (
    <div className="space-y-3">
      {before}
      <div className="relative">
        {back}
        <div className="min-w-0">{title}</div>
      </div>
      {tags && (
        <div className="-mt-2 flex flex-wrap items-center gap-2">{tags}</div>
      )}
      {children}
    </div>
  )
}
