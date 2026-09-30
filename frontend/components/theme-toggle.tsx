"use client"

import { MonitorIcon, MoonIcon, SunIcon } from "lucide-react"
import { useTheme } from "next-themes"

import { Button } from "@/components/ui/button"

const modes = [
  { value: "system", label: "System", icon: MonitorIcon },
  { value: "light", label: "Light", icon: SunIcon },
  { value: "dark", label: "Dark", icon: MoonIcon },
] as const

export function ThemeModes() {
  const { theme, setTheme } = useTheme()

  return (
    <div className="flex w-full gap-1" role="group" aria-label="Theme">
      {modes.map(({ value, label, icon: Icon }) => (
        <Button
          key={value}
          type="button"
          variant={theme === value ? "secondary" : "ghost"}
          className="h-8 flex-1 shrink"
          aria-label={label}
          aria-pressed={theme === value}
          onClick={() => setTheme(value)}
        >
          <Icon />
        </Button>
      ))}
    </div>
  )
}
