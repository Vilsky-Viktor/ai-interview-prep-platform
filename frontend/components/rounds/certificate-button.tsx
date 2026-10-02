"use client"

import Link from "next/link"
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
  if (certificateId) {
    return (
      <Button
        variant="outline"
        nativeButton={false}
        render={<Link href={`/certificates/${certificateId}`} />}
      >
        Certificate
      </Button>
    )
  }

  return (
    <Dialog>
      <DialogTrigger render={<Button variant="outline" />}>
        Certificate
      </DialogTrigger>
      <DialogContent showCloseButton={false} className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>How to earn the certificate</DialogTitle>
        </DialogHeader>
        <CertificateRules />
        <DialogFooter showCloseButton />
      </DialogContent>
    </Dialog>
  )
}

/** The rules come from rounds, which decides who earns a certificate; loaded when shown. */
function CertificateRules() {
  const [rules, setRules] = useState<string[] | null>(null)

  useEffect(() => {
    apiFetch<string[]>("/rounds/certificates/rules")
      .then(setRules)
      .catch(() => setRules([]))
  }, [])

  if (!rules) {
    return <p className="font-light text-muted-foreground">Loading…</p>
  }

  return (
    <ul className="list-disc space-y-2 pl-5 font-light">
      {rules.map((rule) => (
        <li key={rule}>{rule}</li>
      ))}
    </ul>
  )
}
