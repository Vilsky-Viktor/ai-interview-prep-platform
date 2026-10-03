"use client"

import { Combobox } from "@base-ui/react/combobox"
import { CheckIcon, ChevronDownIcon, SearchIcon } from "lucide-react"
import { useTranslations } from "next-intl"
import { useState } from "react"
import { toast } from "sonner"

import { LANGUAGE_NAMES, LOCALES, type Locale } from "@/constants/i18n"
import { apiErrorMessage, apiFetch } from "@/lib/api"
import { auth } from "@/lib/firebase"

/** A dropdown of the languages with a search field, which saves the choice right away. */
export function LanguageSetting({ current }: { current: Locale }) {
  const t = useTranslations("settings")
  const [saving, setSaving] = useState(false)

  async function choose(language: Locale | null) {
    if (!language || language === current) {
      return
    }

    setSaving(true)

    try {
      await apiFetch("/library/me/settings", {
        method: "PUT",
        body: JSON.stringify({ language }),
      })
      // The new token carries the language; auth-provider.tsx switches the interface to it.
      await auth.currentUser?.getIdToken(true)
    } catch (error) {
      toast.error(apiErrorMessage(error, t("languageFailed")))
    } finally {
      setSaving(false)
    }
  }

  return (
    <Combobox.Root
      items={LOCALES}
      value={current}
      onValueChange={choose}
      itemToStringLabel={(locale: Locale) => LANGUAGE_NAMES[locale]}
      disabled={saving}
    >
      <Combobox.Trigger
        aria-label={t("language")}
        className="flex h-12 w-full max-w-xs items-center justify-between gap-3 rounded-full bg-muted/50 px-5 text-base normal-case transition-colors outline-none hover:bg-muted focus-visible:ring-2 focus-visible:ring-ring disabled:opacity-50"
      >
        <Combobox.Value />
        <ChevronDownIcon className="size-5 text-muted-foreground" />
      </Combobox.Trigger>
      <Combobox.Portal>
        <Combobox.Positioner sideOffset={6} align="start" className="z-50">
          <Combobox.Popup className="w-(--anchor-width) overflow-hidden rounded-xl bg-popover text-popover-foreground shadow-md ring-1 ring-foreground/10">
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
              {(locale: Locale) => (
                <Combobox.Item
                  key={locale}
                  value={locale}
                  className="flex cursor-default items-center justify-between gap-2 rounded-lg px-3 py-2 text-base outline-none select-none data-highlighted:bg-accent data-highlighted:text-accent-foreground"
                >
                  {LANGUAGE_NAMES[locale]}
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
