"use client"

import { UploadIcon } from "lucide-react"
import { useRouter } from "next/navigation"
import { useTranslations } from "next-intl"
import { useRef, useState } from "react"
import { toast } from "sonner"

import { InviteExample } from "@/components/company/invite-example"
import { TabNav } from "@/components/tab-nav"
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
import { Textarea } from "@/components/ui/textarea"
import {
  INVITE_EXAMPLES,
  INVITE_TAB_KEY,
  INVITE_TABS,
  type InviteTab,
} from "@/constants/invites"
import {
  MAX_BULK_TEXT_LENGTH,
  MAX_CANDIDATE_NAME_LENGTH,
} from "@/constants/limits"
import { ApiError, apiFetch } from "@/lib/api"
import type { BulkInviteResult } from "@/types/company"

// A field as in "Add member".
const FIELD =
  "rounded-full border border-transparent transition-colors focus-within:border-ring"
const INPUT = "h-16 border-0 px-6 text-lg focus-visible:ring-0 md:text-lg"

/** "New candidate" beside the test's title: a dialog with three tabs, one email with an
 * optional name, a list, or a file. The API reads the emails and names and invites each; what
 * it couldn't stays in the tab with the reasons under it. The last tab used is remembered in
 * this browser. The candidate list (`candidatesHref`) shows the invited after. */
export function InviteCandidate({
  interviewId,
  candidatesHref,
}: {
  interviewId: string
  candidatesHref: string
}) {
  const t = useTranslations("interviews")
  const share = useTranslations("share")
  const common = useTranslations("common")
  const router = useRouter()
  const fileInput = useRef<HTMLInputElement>(null)
  const [open, setOpen] = useState(false)
  const [tab, setTab] = useState<InviteTab>("one")
  const [email, setEmail] = useState("")
  const [name, setName] = useState("")
  const [text, setText] = useState("")
  const [file, setFile] = useState<File | null>(null)
  const [skipped, setSkipped] = useState<BulkInviteResult["skipped"]>([])
  const [error, setError] = useState("")
  const [sending, setSending] = useState(false)

  // The tab last used in this browser, as the dialog opens.
  function openDialog(next: boolean) {
    if (sending) {
      return
    }

    if (next) {
      try {
        const saved = localStorage.getItem(INVITE_TAB_KEY) as InviteTab

        setTab(INVITE_TABS.includes(saved) ? saved : "one")
      } catch {}
    }

    setOpen(next)
  }

  function choose(next: InviteTab) {
    setTab(next)
    setSkipped([])
    setError("")

    try {
      localStorage.setItem(INVITE_TAB_KEY, next)
    } catch {}
  }

  const ready = { one: email.trim(), many: text.trim(), file }[tab]

  async function send(event: React.FormEvent) {
    event.preventDefault()
    setSending(true)
    setError("")

    try {
      const body =
        tab === "one"
          ? { text: email, name }
          : { text: tab === "many" ? text : await file!.text() }
      const result = await apiFetch<BulkInviteResult>(
        `/companies/interviews/${interviewId}/candidates/bulk`,
        { method: "POST", body: JSON.stringify(body) }
      )

      if (result.invited.length > 0) {
        toast.success(
          result.invited.length === 1
            ? share("sent", { email: result.invited[0] })
            : t("invitedMany", { count: result.invited.length })
        )
        router.refresh()
      }

      setSkipped(result.skipped)

      // What wasn't invited from a list stays, to fix or send again later.
      if (tab === "many") {
        setText(result.skipped.map((row) => row.email).join("\n"))
      }

      if (result.skipped.length === 0) {
        setEmail("")
        setName("")
        setFile(null)
        setOpen(false)
        router.push(candidatesHref)
      }
    } catch (failure) {
      // No emails, too many, or a name with several emails: the API says which.
      const invalid = failure instanceof ApiError && failure.status < 500
      setError(invalid ? failure.message : share("failed"))
    } finally {
      setSending(false)
    }
  }

  const reasons = [...new Set(skipped.map((row) => row.reason))]

  return (
    <Dialog open={open} onOpenChange={openDialog}>
      <DialogTrigger
        render={<Button className="h-12 shrink-0 px-6 text-base" />}
      >
        {t("newCandidate")}
      </DialogTrigger>
      <DialogContent showCloseButton={false} className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>{t("newCandidate")}</DialogTitle>
        </DialogHeader>
        <TabNav
          items={INVITE_TABS.map((id) => ({ id, label: t(`inviteTab.${id}`) }))}
          current={tab}
          onSelect={(id) => choose(id as InviteTab)}
        />
        <form id="invite-candidate-form" onSubmit={send} className="space-y-3">
          {tab === "one" && (
            <>
              <div className={FIELD}>
                <Input
                  type="email"
                  autoComplete="off"
                  placeholder="candidate@example.com"
                  aria-label={t("candidateEmail")}
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  className={INPUT}
                />
              </div>
              <div className={FIELD}>
                <Input
                  autoComplete="off"
                  maxLength={MAX_CANDIDATE_NAME_LENGTH}
                  placeholder={t("candidateName")}
                  aria-label={t("candidateName")}
                  value={name}
                  onChange={(event) => setName(event.target.value)}
                  className={INPUT}
                />
              </div>
            </>
          )}
          {tab === "many" && (
            <>
              {/* A list: it grows as one is pasted. */}
              <Textarea
                rows={3}
                maxLength={MAX_BULK_TEXT_LENGTH}
                placeholder="candidate@example.com"
                aria-label={t("candidateEmails")}
                value={text}
                onChange={(event) => {
                  setText(event.target.value)
                  setSkipped([])
                }}
                className="max-h-64 min-h-28 resize-none rounded-[2rem] border-transparent px-6 py-[18px] text-lg focus-visible:border-ring focus-visible:ring-0 md:text-lg"
              />
              <InviteExample />
            </>
          )}
          {tab === "file" && (
            <>
              <Button
                type="button"
                variant="outline"
                className="h-16 w-full justify-start gap-3 rounded-full px-6 text-lg font-normal"
                onClick={() => fileInput.current?.click()}
              >
                <UploadIcon className="size-5 shrink-0 text-muted-foreground" />
                <span className="truncate normal-case">
                  {file ? file.name : t("uploadFile")}
                </span>
              </Button>
              <input
                ref={fileInput}
                type="file"
                accept=".csv,.txt,text/csv,text/plain"
                className="hidden"
                onChange={(event) => {
                  setFile(event.target.files?.[0] ?? null)
                  setSkipped([])
                  setError("")
                  event.target.value = ""
                }}
              />
              <p className="px-6 py-2 text-center text-sm text-muted-foreground">
                {t("fileFormats")}
              </p>
              <div className="flex justify-center gap-3">
                {INVITE_EXAMPLES.map((example) => (
                  <Button
                    key={example.href}
                    variant="outline"
                    className="h-10 px-5 text-base"
                    render={<a href={example.href} download />}
                    nativeButton={false}
                  >
                    {t(example.label)}
                  </Button>
                ))}
              </div>
            </>
          )}
          {error && <p className="px-6 text-sm text-destructive">{error}</p>}
          {reasons.length > 0 && (
            <ul className="space-y-1 px-6 text-sm text-destructive">
              {reasons.map((reason) => (
                <li key={reason}>
                  {t(`skip.${reason}`, {
                    count: skipped.filter((row) => row.reason === reason)
                      .length,
                  })}
                </li>
              ))}
            </ul>
          )}
        </form>
        <DialogFooter>
          <DialogClose
            render={
              <Button
                variant="outline"
                className="h-10 px-5 text-base"
                disabled={sending}
              />
            }
          >
            {common("cancel")}
          </DialogClose>
          <Button
            type="submit"
            form="invite-candidate-form"
            className="h-10 px-5 text-base"
            disabled={sending || !ready}
          >
            {t("invite")}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
