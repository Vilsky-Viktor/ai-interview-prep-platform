"use client"

import Link from "next/link"

import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { CERTIFICATE_RULES } from "@/constants/rounds"

export function CertificateButton({ certificateId }: { certificateId: string | null }) {
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
      <DialogTrigger render={<Button variant="outline" />}>Certificate</DialogTrigger>
      <DialogContent showCloseButton={false} className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>How to earn the certificate</DialogTitle>
        </DialogHeader>
        <ul className="list-disc space-y-2 pl-5 font-light">
          {CERTIFICATE_RULES.map((rule) => (
            <li key={rule}>{rule}</li>
          ))}
        </ul>
        <DialogFooter showCloseButton />
      </DialogContent>
    </Dialog>
  )
}
