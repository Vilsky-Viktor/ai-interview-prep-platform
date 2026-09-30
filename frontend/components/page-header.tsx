import type { ReactNode } from "react"

export function PageHeader({
  back,
  before,
  title,
  children,
}: {
  back: ReactNode
  before?: ReactNode
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
      {children}
    </div>
  )
}
