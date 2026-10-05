/** One block of a settings page: a title, a short note and its controls; `action`, when given,
 * sits on the right of all of it, centered vertically. */
export function SettingsSection({
  title,
  description,
  action,
  children,
}: {
  title: string
  description: string
  action?: React.ReactNode
  children?: React.ReactNode
}) {
  return (
    <section className="flex items-center gap-6 rounded-2xl border p-6">
      <div className="min-w-0 flex-1 space-y-4">
        <div className="space-y-1">
          <h2 className="text-lg font-medium">{title}</h2>
          <p className="text-sm text-muted-foreground">{description}</p>
        </div>
        {children}
      </div>
      {action}
    </section>
  )
}
