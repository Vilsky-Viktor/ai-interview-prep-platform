"use client"

import { type ReactNode, useState } from "react"

import { TabNav } from "@/components/tab-nav"

/** Sections of a page as tabs (the site's TabNav as buttons), the first open: each panel's
 * content is made by the page, so a server page can pass its own. */
export function TabPanels({
  panels,
}: {
  panels: { id: string; label: string; content: ReactNode }[]
}) {
  const [current, setCurrent] = useState(panels[0]?.id ?? "")

  return (
    <div className="space-y-6">
      <TabNav
        items={panels.map(({ id, label }) => ({ id, label, keepCase: true }))}
        current={current}
        onSelect={setCurrent}
      />
      {panels.find((panel) => panel.id === current)?.content}
    </div>
  )
}
