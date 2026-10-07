"use client"

import { XIcon } from "lucide-react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { useTranslations } from "next-intl"
import { useState } from "react"
import { toast } from "sonner"

import { LinkJob } from "@/components/company/ats-link-job"
import { ConfirmDialog } from "@/components/confirm-dialog"
import { Button } from "@/components/ui/button"
import { apiErrorMessage, apiFetch } from "@/lib/api"
import type { AtsJobLink, Interview } from "@/types/company"

/** The ATS's jobs linked to the company's interviews, on the ATS's own page, with "Link a job"
 * for owners and admins. */
export function AtsJobLinks({
  companyId,
  links,
  interviews,
  canEdit,
}: {
  companyId: string
  links: AtsJobLink[]
  interviews: Interview[]
  canEdit: boolean
}) {
  const t = useTranslations("ats")

  return (
    <section className="space-y-4">
      <div className="flex items-center justify-between gap-4">
        <div className="space-y-1">
          <h2 className="font-heading text-2xl font-medium">{t("links")}</h2>
          <p className="text-base text-muted-foreground">{t("linksText")}</p>
        </div>
        {canEdit && <LinkJob companyId={companyId} interviews={interviews} />}
      </div>
      {links.length === 0 ? (
        <p className="rounded-2xl border p-6 text-muted-foreground">
          {t("noLinks")}
        </p>
      ) : (
        <ul className="divide-y rounded-2xl border">
          {links.map((link) => (
            <LinkRow
              key={link.id}
              companyId={companyId}
              link={link}
              canEdit={canEdit}
            />
          ))}
        </ul>
      )}
    </section>
  )
}

function LinkRow({
  companyId,
  link,
  canEdit,
}: {
  companyId: string
  link: AtsJobLink
  canEdit: boolean
}) {
  const t = useTranslations("ats")
  const router = useRouter()
  const [confirming, setConfirming] = useState(false)
  const [busy, setBusy] = useState(false)

  async function unlink() {
    setBusy(true)

    try {
      await apiFetch(
        `/companies/ats/links/${link.id}?company_id=${companyId}`,
        {
          method: "DELETE",
        }
      )
      setConfirming(false)
      router.refresh()
    } catch (error) {
      toast.error(apiErrorMessage(error, t("unlinkFailed")))
    } finally {
      setBusy(false)
    }
  }

  return (
    <li className="flex items-center justify-between gap-6 p-4 sm:p-6">
      <span className="min-w-0 space-y-1">
        <span className="block text-lg font-medium">{link.job_name}</span>
        <span className="block text-base text-muted-foreground">
          {t("linkLine", { stage: link.stage_name })}{" "}
          <Link
            href={`/companies/${companyId}/interviews/${link.interview_id}`}
            className="text-foreground underline-offset-4 hover:underline"
          >
            {link.interview_title ?? t("generatingInterview")}
          </Link>
        </span>
        <CandidateCounts companyId={companyId} link={link} canEdit={canEdit} />
      </span>
      {canEdit && (
        <Button
          variant="ghost"
          size="icon"
          className="size-12 shrink-0 text-muted-foreground hover:text-destructive"
          aria-label={t("unlink")}
          onClick={() => setConfirming(true)}
        >
          <XIcon className="size-6" />
        </Button>
      )}
      <ConfirmDialog
        open={confirming}
        onOpenChange={setConfirming}
        title={t("unlinkTitle")}
        text={t("unlinkText", { job: link.job_name })}
        confirm={t("unlink")}
        busy={busy}
        onConfirm={unlink}
      />
    </li>
  )
}

/** How the candidates Workable sent for this job went: invited, waiting for the interview to be
 * ready, and not invited (in red, with "Invite again" for owners and admins). */
function CandidateCounts({
  companyId,
  link,
  canEdit,
}: {
  companyId: string
  link: AtsJobLink
  canEdit: boolean
}) {
  const t = useTranslations("ats")
  const router = useRouter()
  const [busy, setBusy] = useState(false)

  if (!link.invited && !link.waiting && !link.not_invited) {
    return null
  }

  async function retry() {
    setBusy(true)

    try {
      await apiFetch(
        `/companies/ats/candidates/retry?company_id=${companyId}`,
        {
          method: "POST",
        }
      )
      router.refresh()
    } catch (error) {
      toast.error(apiErrorMessage(error, t("inviteAgainFailed")))
    } finally {
      setBusy(false)
    }
  }

  return (
    <span className="flex flex-wrap items-center gap-x-3 gap-y-1 text-sm text-muted-foreground">
      {link.invited > 0 && (
        <span>{t("invitedCount", { count: link.invited })}</span>
      )}
      {link.waiting > 0 && (
        <span>{t("waitingCount", { count: link.waiting })}</span>
      )}
      {link.not_invited > 0 && (
        <span className="text-destructive">
          {t("notInvitedCount", { count: link.not_invited })}
        </span>
      )}
      {link.not_invited > 0 && canEdit && (
        <button
          type="button"
          disabled={busy}
          onClick={retry}
          className="cursor-pointer text-primary lowercase transition-opacity hover:opacity-70 disabled:opacity-50"
        >
          {t("inviteAgain")}
        </button>
      )}
    </span>
  )
}
