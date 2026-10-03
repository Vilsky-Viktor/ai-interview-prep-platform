"use client"

import { useTranslations } from "next-intl"

import { LegalConsent } from "@/components/legal-consent"
import { Button } from "@/components/ui/button"
import { signIn } from "@/lib/auth"

export function SignInPrompt({ message }: { message: string }) {
  const t = useTranslations("signIn")

  return (
    <div className="mx-auto flex w-full max-w-lg flex-col items-center gap-6 rounded-2xl border p-12 text-center">
      <p className="text-base text-muted-foreground">{message}</p>
      <Button
        size="lg"
        className="h-12 px-5 text-base"
        onClick={() => signIn(t("failed"))}
      >
        <span className="font-light">{t("with")}</span>{" "}
        {/* Google's name keeps its capital inside the lowercase button. */}
        <span className="normal-case">Google</span>
      </Button>
      <LegalConsent />
    </div>
  )
}
