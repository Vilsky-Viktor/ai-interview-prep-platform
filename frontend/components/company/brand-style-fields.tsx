"use client"

import { useTranslations } from "next-intl"
import { useState } from "react"

import { PillSelect } from "@/components/pill-select"
import { Input } from "@/components/ui/input"
import { BRAND_FONTS } from "@/constants/brand-fonts"
import type { BrandStyle } from "@/types/company"

// The rounding companies takes, in px.
const MAX_RADIUS = 24

/** The font of all the text on the company's candidates' pages, and how round their cards' and
 * buttons' corners are: the same in both themes, saved with the colors. A rounding counts once
 * it's a whole number within bounds. */
export function BrandStyleFields({
  look,
  onChange,
}: {
  look: BrandStyle
  onChange: (look: BrandStyle) => void
}) {
  const t = useTranslations("brand")

  return (
    // The font, then the roundings on their own line.
    <div className="flex flex-col gap-6" data-testid="brand-style">
      <PillSelect
        label={t("font")}
        value={look.font}
        options={Object.entries(BRAND_FONTS)
          .map(([value, font]) => ({
            value,
            label: font.label,
            fontFamily: font.family ?? "var(--font-poppins)",
          }))
          .sort((a, b) =>
            a.value === "poppins_geist" || b.value === "poppins_geist"
              ? Number(b.value === "poppins_geist") -
                Number(a.value === "poppins_geist")
              : a.label.localeCompare(b.label)
          )}
        onChange={(font) =>
          onChange({ ...look, font: font as BrandStyle["font"] })
        }
        pillClassName="w-72 justify-between"
      />
      <div className="flex gap-4">
        <RadiusField
          label={t("radius")}
          value={look.radius}
          onChange={(radius) => onChange({ ...look, radius })}
        />
        <RadiusField
          label={t("buttonRadius")}
          value={look.button_radius}
          onChange={(button_radius) => onChange({ ...look, button_radius })}
        />
      </div>
    </div>
  )
}

function RadiusField({
  label,
  value,
  onChange,
}: {
  label: string
  value: number
  onChange: (value: number) => void
}) {
  const [typed, setTyped] = useState<string | null>(null)

  return (
    <label className="flex flex-col gap-2">
      <span className="text-sm text-muted-foreground">{label}</span>
      <span className="flex items-center gap-2">
        <Input
          type="number"
          min={0}
          max={MAX_RADIUS}
          value={typed ?? String(value)}
          className="w-20 border-transparent"
          onChange={(event) => {
            const next = Number(event.target.value)
            setTyped(event.target.value)

            if (
              event.target.value !== "" &&
              Number.isInteger(next) &&
              next >= 0 &&
              next <= MAX_RADIUS
            ) {
              onChange(next)
            }
          }}
          onBlur={() => setTyped(null)}
        />
        <span className="text-sm text-muted-foreground">px</span>
      </span>
    </label>
  )
}
