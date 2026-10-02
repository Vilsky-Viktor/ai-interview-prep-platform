import Link from "next/link"

/** Shown wherever someone signs in: signing in accepts the terms. */
export function LegalConsent() {
  return (
    <p className="text-sm text-muted-foreground">
      By signing in, you agree to the{" "}
      <Link href="/terms" className="underline underline-offset-4">
        Terms
      </Link>{" "}
      and the{" "}
      <Link href="/privacy" className="underline underline-offset-4">
        Privacy policy
      </Link>
      .
    </p>
  )
}
