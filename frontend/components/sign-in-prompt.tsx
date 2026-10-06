"use client"

import { useTranslations } from "next-intl"

import { SignInOptions } from "@/components/sign-in-options"

/** A page that only asks to sign in: a title, the reason when there's more to say, and the ways
 * to sign in right there. */
export function SignInPrompt({ message }: { message?: string }) {
  const t = useTranslations("signIn")

  return (
    <div className="mx-auto flex w-full max-w-md flex-col items-center gap-6 rounded-2xl border p-10 text-center">
      <div className="space-y-2">
        <h2 className="font-heading text-2xl font-medium tracking-tight">
          {t("title")}
        </h2>
        {message && (
          <p className="text-base text-muted-foreground">{message}</p>
        )}
      </div>
      <div className="w-full">
        <SignInOptions />
      </div>
    </div>
  )
}
