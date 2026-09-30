import Link from "next/link"

import { Button } from "@/components/ui/button"

export function CompanyNav({
  companyId,
  current,
}: {
  companyId: string
  current: "interviews" | "members"
}) {
  const items = [
    {
      id: "interviews",
      href: `/company/${companyId}/interviews`,
      label: "Interviews",
    },
    {
      id: "members",
      href: `/company/${companyId}/members`,
      label: "Admins",
    },
  ] as const

  return (
    <nav className="flex w-full rounded-lg border p-2">
      {items.map((item) => (
        <Button
          key={item.id}
          variant={item.id === current ? "secondary" : "ghost"}
          className="h-12 flex-1 px-6 text-base"
          nativeButton={false}
          render={<Link href={item.href} />}
          aria-current={item.id === current ? "page" : undefined}
        >
          {item.label}
        </Button>
      ))}
    </nav>
  )
}
