"use client"

import { ArrowRightIcon } from "lucide-react"
import { useRouter } from "next/navigation"
import { useTranslations } from "next-intl"
import { useState } from "react"
import { toast } from "sonner"

import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { WORKABLE_SCOPES, WORKABLE_TOKEN_PATH } from "@/constants/ats"
import { apiErrorMessage, apiFetch } from "@/lib/api"

/** Connect (or Reconnect): Workable's address and an API access token, checked by the API
 * before it's saved. */
export function ConnectWorkable({
  companyId,
  again,
}: {
  companyId: string
  again: boolean
}) {
  const t = useTranslations("ats")
  const common = useTranslations("common")
  const router = useRouter()
  const [open, setOpen] = useState(false)
  const [account, setAccount] = useState("")
  const [token, setToken] = useState("")
  const [saving, setSaving] = useState(false)

  async function connect(event: React.FormEvent) {
    event.preventDefault()
    setSaving(true)

    try {
      await apiFetch(`/companies/ats/workable?company_id=${companyId}`, {
        method: "PUT",
        body: JSON.stringify({ account, token }),
      })
      setOpen(false)
      setToken("")
      router.refresh()
    } catch (error) {
      toast.error(apiErrorMessage(error, t("connectFailed")))
    } finally {
      setSaving(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={(next) => !saving && setOpen(next)}>
      <DialogTrigger render={<Button className="h-10 px-5 text-base" />}>
        {again ? t("reconnect") : t("connect")}
      </DialogTrigger>
      <DialogContent showCloseButton={false} className="sm:max-w-2xl">
        <DialogHeader>
          <DialogTitle>{t("connectTitle")}</DialogTitle>
        </DialogHeader>
        <ConnectSteps />
        <form id="connect-workable" onSubmit={connect} className="space-y-3">
          {/* The fields as in "Add member". */}
          <div className="rounded-full border border-transparent transition-colors focus-within:border-ring">
            <Input
              required
              maxLength={200}
              placeholder="acme.workable.com"
              aria-label={t("account")}
              value={account}
              onChange={(event) => setAccount(event.target.value)}
              className="h-16 border-0 px-6 text-lg focus-visible:ring-0 md:text-lg"
            />
          </div>
          <div className="rounded-full border border-transparent transition-colors focus-within:border-ring">
            <Input
              required
              type="password"
              autoComplete="off"
              maxLength={500}
              placeholder={t("token")}
              aria-label={t("token")}
              value={token}
              onChange={(event) => setToken(event.target.value)}
              className="h-16 border-0 px-6 text-lg focus-visible:ring-0 md:text-lg"
            />
          </div>
        </form>
        <DialogFooter>
          <DialogClose
            render={
              <Button
                variant="outline"
                className="h-10 px-5 text-base"
                disabled={saving}
              />
            }
          >
            {common("cancel")}
          </DialogClose>
          <Button
            type="submit"
            form="connect-workable"
            className="h-10 px-5 text-base"
            disabled={saving || !account || !token}
          >
            {t("connect")}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

/** Where to make the token in Workable, step by step: its menus and scopes as Workable names
 * them, in chips like code in questions. */
function ConnectSteps() {
  const t = useTranslations("ats")
  const chip =
    "rounded bg-muted px-1.5 py-0.5 font-mono text-sm text-foreground"

  return (
    <ol className="list-decimal space-y-3 ps-5 text-base text-muted-foreground">
      <li className="space-y-1.5">
        <span className="block">{t("stepOpen")}</span>
        <span className="flex flex-wrap items-center gap-1.5">
          {WORKABLE_TOKEN_PATH.map((item, index) => (
            <span key={item} className="flex items-center gap-1.5">
              {index > 0 && (
                <ArrowRightIcon aria-hidden className="size-4 rtl:rotate-180" />
              )}
              <span className={chip}>{item}</span>
            </span>
          ))}
        </span>
      </li>
      <li className="space-y-1.5">
        <span className="block">{t("stepScopes")}</span>
        <span className="flex flex-wrap gap-1.5">
          {WORKABLE_SCOPES.map((scope) => (
            <span key={scope} className={chip}>
              {scope}
            </span>
          ))}
        </span>
      </li>
      <li>{t("stepPaste")}</li>
    </ol>
  )
}
