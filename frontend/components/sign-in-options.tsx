"use client"

import { useTranslations } from "next-intl"
import { useState } from "react"
import { toast } from "sonner"

import { LegalConsent } from "@/components/legal-consent"
import { LinkedInIcon } from "@/components/linkedin-icon"
import { GitHubIcon, GoogleIcon } from "@/components/sign-in-icons"
import { Button } from "@/components/ui/button"
import { SIGN_IN_PROVIDERS } from "@/constants/auth"
import { signIn } from "@/lib/auth"
import type { SignInProvider } from "@/types/sign-in"

const NAMES: Record<SignInProvider, string> = {
  google: "Google",
  linkedin: "LinkedIn",
  github: "GitHub",
}

const ICONS: Record<SignInProvider, () => React.ReactNode> = {
  google: GoogleIcon,
  linkedin: () => <LinkedInIcon className="size-5" />,
  github: GitHubIcon,
}

/** The ways to sign in, Google, LinkedIn or GitHub, one account per email whichever is used;
 * the sign-in dialog shows them, and so does a page that only asks to sign in. `onSignedIn`
 * runs once signed in. */
export function SignInOptions({ onSignedIn }: { onSignedIn?: () => void }) {
  const t = useTranslations("signIn")
  const [busy, setBusy] = useState(false)
  // The way just tried, when its email already has an account under another way.
  const [linking, setLinking] = useState<SignInProvider | null>(null)

  async function choose(name: SignInProvider) {
    setBusy(true)
    const result = await signIn(name)
    setBusy(false)

    if (result === "done") {
      onSignedIn?.()
    } else if (result === "verify") {
      toast.info(t("verify"))
      onSignedIn?.()
    } else if (result === "link") {
      setLinking(name)
    } else if (result === "failed") {
      toast.error(t("failed"))
    }
  }

  return (
    <div className="w-full space-y-4">
      {/* Only when the email already has an account under another way. */}
      {linking && (
        <p role="status" className="text-sm text-muted-foreground">
          {t("link", { provider: NAMES[linking] })}
        </p>
      )}
      <div className="space-y-3">
        {SIGN_IN_PROVIDERS.filter((name) => name !== linking).map((name) => {
          const Icon = ICONS[name]

          return (
            <Button
              key={name}
              variant="outline"
              className="h-12 w-full gap-3 text-base"
              disabled={busy}
              onClick={() => choose(name)}
            >
              <Icon />
              {/* One phrase, so each language puts the name where it belongs; the name keeps
                  its capitals inside the lowercase button. */}
              <span>
                {t.rich("continueWith", {
                  provider: NAMES[name],
                  name: (chunks) => (
                    <span className="normal-case">{chunks}</span>
                  ),
                })}
              </span>
            </Button>
          )
        })}
      </div>
      {/* Set a little apart from the buttons. */}
      <div className="pt-2">
        <LegalConsent />
      </div>
    </div>
  )
}
