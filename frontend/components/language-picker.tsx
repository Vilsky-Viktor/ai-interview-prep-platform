"use client"

import { Combobox } from "@base-ui/react/combobox"
import { cn } from "cn"
import { CheckIcon, ChevronDownIcon, SearchIcon } from "lucide-react"
import { useTranslations } from "next-intl"

import { LANGUAGE_NAMES, type Locale } from "@/constants/i18n"

/** A dropdown of languages with a search field, each named in its own language. `compact` is
 * the small trigger that sits next to a text box's send button. */
export function LanguagePicker({
  languages,
  value,
  onChange,
  label,
  disabled = false,
  compact = false,
}: {
  languages: readonly Locale[]
  value: Locale
  onChange: (language: Locale) => void
  label: string
  disabled?: boolean
  compact?: boolean
}) {
  const t = useTranslations("settings")

  return (
    <Combobox.Root
      items={languages}
      value={value}
      onValueChange={(language: Locale | null) => {
        if (language && language !== value) {
          onChange(language)
        }
      }}
      itemToStringLabel={(language: Locale) => LANGUAGE_NAMES[language]}
      disabled={disabled}
    >
      <Combobox.Trigger
        aria-label={label}
        className={cn(
          "flex items-center justify-between gap-3 rounded-full bg-muted/50 normal-case transition-colors outline-none hover:bg-muted focus-visible:ring-2 focus-visible:ring-ring disabled:opacity-50",
          compact
            ? "h-9 w-40 px-4 text-sm"
            : "h-12 w-full max-w-xs px-5 text-base"
        )}
      >
        <Combobox.Value />
        <ChevronDownIcon
          className={cn("text-muted-foreground", compact ? "size-4" : "size-5")}
        />
      </Combobox.Trigger>
      <Combobox.Portal>
        <Combobox.Positioner sideOffset={6} align="start" className="z-50">
          <Combobox.Popup className="w-(--anchor-width) min-w-56 overflow-hidden rounded-xl bg-popover text-popover-foreground shadow-md ring-1 ring-foreground/10">
            <div className="flex items-center gap-2 border-b px-3">
              <SearchIcon className="size-4 text-muted-foreground" />
              <Combobox.Input
                placeholder={t("searchLanguage")}
                className="h-11 w-full bg-transparent text-base outline-none placeholder:text-muted-foreground"
              />
            </div>
            <Combobox.Empty className="px-4 py-3 text-sm text-muted-foreground empty:hidden">
              {t("noLanguage")}
            </Combobox.Empty>
            <Combobox.List className="max-h-64 overflow-y-auto p-1">
              {(language: Locale) => (
                <Combobox.Item
                  key={language}
                  value={language}
                  className="flex cursor-default items-center justify-between gap-2 rounded-lg px-3 py-2 text-base outline-none select-none data-highlighted:bg-accent data-highlighted:text-accent-foreground"
                >
                  {LANGUAGE_NAMES[language]}
                  <Combobox.ItemIndicator>
                    <CheckIcon className="size-4" />
                  </Combobox.ItemIndicator>
                </Combobox.Item>
              )}
            </Combobox.List>
          </Combobox.Popup>
        </Combobox.Positioner>
      </Combobox.Portal>
    </Combobox.Root>
  )
}
