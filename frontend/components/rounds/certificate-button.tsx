"use client"

import Link from "next/link"
import { useTranslations } from "next-intl"
import { useEffect, useState } from "react"

import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { apiFetch } from "@/lib/api"

export function CertificateButton({
  certificateId,
}: {
  certificateId: string | null
}) {
  const t = useTranslations("certificate")

  if (certificateId) {
    return (
      <Button
        variant="outline"
        nativeButton={false}
        render={<Link href={`/certificates/${certificateId}`} />}
      >
        {t("title")}
      </Button>
    )
  }

  return (
    <Dialog>
      <DialogTrigger render={<Button variant="outline" />}>
        {t("title")}
      </DialogTrigger>
      <DialogContent showCloseButton={false} className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>{t("howTo")}</DialogTitle>
        </DialogHeader>
        <CertificateRules />
        <DialogFooter showCloseButton />
      </DialogContent>
    </Dialog>
  )
}

/** The rules come from rounds, which decides who earns a certificate; loaded when shown. */
function CertificateRules() {
  const common = useTranslations("common")
  const [rules, setRules] = useState<string[] | null>(null)

  useEffect(() => {
    apiFetch<string[]>("/rounds/certificates/rules")
      .then(setRules)
      .catch(() => setRules([]))
  }, [])

  if (!rules) {
    return (
      <p className="font-light text-muted-foreground">{common("loading")}</p>
    )
  }

  return (
    <ul className="list-disc space-y-2 ps-5 font-light">
      {rules.map((rule) => (
        <li key={rule}>{rule}</li>
      ))}
    </ul>
  )
}
