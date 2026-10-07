"use client"

import { InfoIcon } from "lucide-react"
import { useTranslations } from "next-intl"

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
import type { AtsProvider } from "@/constants/ats"

/** The ATS's one info button, beside Connect: a dialog with everything to know, connected or
 * not: how candidates come from the ATS and what goes back, step by step, after any setup still
 * to do there (`children`: Greenhouse's web hook). */
export function CandidateFlow({
  provider,
  open,
  onOpenChange,
  children,
}: {
  provider: AtsProvider
  open: boolean
  onOpenChange: (open: boolean) => void
  children?: React.ReactNode
}) {
  const t = useTranslations("ats")
  const common = useTranslations("common")

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogTrigger
        render={
          <Button
            variant="ghost"
            size="icon"
            className="size-10 shrink-0 text-muted-foreground"
            aria-label={t("flowTitle", { ats: provider.name })}
          />
        }
      >
        <InfoIcon className="size-6" />
      </DialogTrigger>
      <DialogContent
        showCloseButton={false}
        className="max-h-[90dvh] overflow-y-auto sm:max-w-2xl"
      >
        <DialogHeader>
          <DialogTitle>{t("flowTitle", { ats: provider.name })}</DialogTitle>
        </DialogHeader>
        {children}
        {/* Under the setup, the flow gets its own heading. */}
        {children && <h3 className="text-lg font-medium">{t("flowHow")}</h3>}
        <ol className="list-decimal space-y-3 ps-5 text-base text-muted-foreground">
          {(
            [
              "flowStage",
              "flowLink",
              "flowMove",
              "flowInvite",
              "flowFinish",
              "flowDecide",
            ] as const
          ).map((step) => (
            <li key={step}>{t(step, { ats: provider.name })}</li>
          ))}
        </ol>
        <DialogFooter>
          <DialogClose
            render={
              <Button variant="outline" className="h-10 px-5 text-base" />
            }
          >
            {common("close")}
          </DialogClose>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
