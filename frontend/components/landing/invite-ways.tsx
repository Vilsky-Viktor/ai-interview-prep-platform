import { cn } from "cn"
import {
  CopyIcon,
  FileUpIcon,
  LinkIcon,
  MailIcon,
  WorkflowIcon,
} from "lucide-react"
import { getTranslations } from "next-intl/server"

import { KeepAcronyms } from "@/components/keep-acronyms"
import { LandingSection } from "@/components/landing/section"
import { ATS_PROVIDERS } from "@/constants/ats"

const WAYS = [
  { key: "email", Icon: MailIcon },
  { key: "list", Icon: FileUpIcon },
  { key: "link", Icon: LinkIcon },
  { key: "ats", Icon: WorkflowIcon },
] as const

// A field as the invite dialog and the shareable link have it.
const FIELD =
  "flex h-12 min-w-0 items-center gap-3 rounded-full bg-muted px-5 text-base dark:bg-input/30"

/** The four ways candidates get an interview, each as a card like the advantages' with a small
 * piece of the screen it happens on: the invite dialog's emails and its file upload
 * (components/company/invite-candidate.tsx), the shareable link (share-link.tsx) and the ATSs
 * that send candidates in. */
export async function InviteWaysSection() {
  const t = await getTranslations("landing.invite")

  return (
    <LandingSection title={t("title")} text={t("text")}>
      <ul className="mx-auto mt-8 grid w-full max-w-4xl grid-cols-1 gap-8 pe-4 sm:grid-cols-2 sm:pe-0">
        {WAYS.map(({ key, Icon }) => (
          <li
            key={key}
            className="relative flex flex-col gap-5 rounded-2xl border bg-background p-6"
          >
            {/* The icon over the card's top end corner, as on the advantages' cards. */}
            <span className="absolute -end-7 -top-7 flex size-20 items-center justify-center rounded-full bg-background">
              <Icon aria-hidden className="size-12 text-primary" />
            </span>
            <span className="block space-y-1">
              <span className="block text-base font-medium whitespace-nowrap lowercase">
                <KeepAcronyms text={t(`ways.${key}.title`)} />
                <span className="text-primary">.</span>
              </span>
              <span className="block text-base text-muted-foreground">
                {t(`ways.${key}.text`)}
              </span>
            </span>
            {/* Pushed to the card's bottom, so the pieces line up across a row. */}
            <span aria-hidden className="mt-auto block">
              <WayPreview way={key} />
            </span>
          </li>
        ))}
      </ul>
    </LandingSection>
  )
}

function WayPreview({ way }: { way: (typeof WAYS)[number]["key"] }) {
  if (way === "email") {
    return <span className={FIELD}>anna@example.com</span>
  }

  if (way === "list") {
    return (
      <span className={cn(FIELD, "justify-between")}>
        <span className="truncate">candidates.csv</span>
        <FileUpIcon className="size-5 shrink-0 text-muted-foreground" />
      </span>
    )
  }

  if (way === "link") {
    return (
      <span className={cn(FIELD, "justify-between")}>
        <span className="truncate" dir="ltr">
          prepza.ai/apply/k7Q2x9
        </span>
        <CopyIcon className="size-5 shrink-0 text-muted-foreground" />
      </span>
    )
  }

  return (
    <span className="flex h-12 items-center gap-4">
      {ATS_PROVIDERS.map((provider) => (
        // eslint-disable-next-line @next/next/no-img-element
        <img
          key={provider.id}
          src={provider.logo}
          alt=""
          className="size-8 rounded-md object-contain"
        />
      ))}
    </span>
  )
}
