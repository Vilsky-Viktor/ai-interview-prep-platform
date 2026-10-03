"use client"

import { ChevronDownIcon } from "lucide-react"
import { useRouter } from "next/navigation"
import { useLocale, useTranslations } from "next-intl"
import { useEffect, useState } from "react"
import { toast } from "sonner"

import { useAuth } from "@/components/auth-provider"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { apiErrorMessage, apiFetch } from "@/lib/api"
import { openCheckout } from "@/lib/paddle"
import type { AutoTopUp, Catalog } from "@/types/billing"

function PillSelect({
  label,
  value,
  options,
  onChange,
}: {
  label: string
  value: string
  options: { value: string; label: string }[]
  onChange: (value: string) => void
}) {
  return (
    <label className="block space-y-2">
      <span className="text-sm text-muted-foreground">{label}</span>
      <span className="relative block rounded-full border border-transparent transition-colors focus-within:border-ring">
        <select
          value={value}
          onChange={(event) => onChange(event.target.value)}
          className="h-14 w-full appearance-none rounded-full border-0 bg-transparent px-6 pr-16 text-lg outline-none dark:bg-input/30"
        >
          {options.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
        <ChevronDownIcon
          aria-hidden
          className="pointer-events-none absolute top-1/2 right-6 size-6 -translate-y-1/2 text-muted-foreground"
        />
      </span>
    </label>
  )
}

/** A wallet's automatic top-up: what it is now, and a dialog to turn it on, change or turn
 * off. Turning it on the first time opens Paddle's checkout to save the card. */
export function AutoTopUpSetting({
  catalog,
  companyId,
}: {
  catalog: Catalog
  companyId?: string
}) {
  const t = useTranslations("autoTopUp")
  const common = useTranslations("common")
  const locale = useLocale()
  const router = useRouter()
  const { user } = useAuth()
  const path = companyId
    ? `/companies/companies/${companyId}/auto-top-up`
    : "/billing/me/auto-top-up"
  const [setting, setSetting] = useState<AutoTopUp | null>(null)
  const [open, setOpen] = useState(false)
  const [product, setProduct] = useState("")
  const [threshold, setThreshold] = useState("")
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    apiFetch<AutoTopUp>(path)
      .then(setSetting)
      .catch(() => {})
  }, [path])

  if (!setting?.offered || !user) {
    return null
  }

  const titles = Object.fromEntries(
    catalog.products.map((item) => [item.key, item.title])
  )
  const credits = (count: number) => count.toLocaleString(locale)

  function handleOpen(next: boolean) {
    if (saving || !setting) {
      return
    }

    setOpen(next)
    setProduct(setting.product ?? setting.products[0] ?? "")
    setThreshold(String(setting.threshold ?? setting.thresholds[0] ?? ""))
  }

  async function save(event: React.FormEvent) {
    event.preventDefault()
    setSaving(true)

    try {
      const saved = await apiFetch<AutoTopUp>(path, {
        method: "PUT",
        body: JSON.stringify({ product, threshold: Number(threshold) }),
      })
      setSetting(saved)
      setOpen(false)

      if (!saved.checkout) {
        toast.success(t("saved"))

        return
      }

      await openCheckout(
        catalog,
        saved.checkout.price_id,
        saved.checkout.custom_data,
        user!.email,
        () => {
          toast.success(t("turnedOn"))
          // Paddle confirms the subscription within seconds.
          window.setTimeout(() => {
            apiFetch<AutoTopUp>(path).then(setSetting)
            router.refresh()
          }, 4000)
        }
      )
    } catch (error) {
      toast.error(apiErrorMessage(error, t("failed")))
    } finally {
      setSaving(false)
    }
  }

  async function turnOff() {
    setSaving(true)

    try {
      await apiFetch(path, { method: "DELETE" })
      setSetting(await apiFetch<AutoTopUp>(path))
      setOpen(false)
      toast.success(t("turnedOff"))
    } catch (error) {
      toast.error(apiErrorMessage(error, t("failed")))
    } finally {
      setSaving(false)
    }
  }

  const summary =
    setting.on && setting.product && setting.threshold
      ? t("on", {
          amount: titles[setting.product] ?? setting.product,
          threshold: credits(setting.threshold),
        })
      : setting.waiting
        ? t("waiting")
        : t("off")

  return (
    <Dialog open={open} onOpenChange={handleOpen}>
      <DialogTrigger
        render={
          <button
            type="button"
            className="text-left text-sm text-muted-foreground underline-offset-4 hover:text-foreground hover:underline"
          />
        }
      >
        {summary}
      </DialogTrigger>
      <DialogContent showCloseButton={false} className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>{t("title")}</DialogTitle>
          <DialogDescription>{t("text")}</DialogDescription>
        </DialogHeader>
        <form id="auto-top-up-form" onSubmit={save} className="space-y-4">
          <PillSelect
            label={t("amount")}
            value={product}
            onChange={setProduct}
            options={setting.products.map((key) => ({
              value: key,
              label: titles[key] ?? key,
            }))}
          />
          <PillSelect
            label={t("when")}
            value={threshold}
            onChange={setThreshold}
            options={setting.thresholds.map((value) => ({
              value: String(value),
              label: t("under", { threshold: credits(value) }),
            }))}
          />
        </form>
        <DialogFooter>
          {setting.on || setting.waiting ? (
            <Button
              variant="outline"
              className="h-10 px-5 text-base"
              disabled={saving}
              onClick={turnOff}
            >
              {t("turnOff")}
            </Button>
          ) : (
            <Button
              variant="outline"
              className="h-10 px-5 text-base"
              disabled={saving}
              onClick={() => setOpen(false)}
            >
              {common("cancel")}
            </Button>
          )}
          <Button
            type="submit"
            form="auto-top-up-form"
            className="h-10 px-5 text-base"
            disabled={saving || !product || !threshold}
          >
            {setting.on ? t("save") : t("turnOn")}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
