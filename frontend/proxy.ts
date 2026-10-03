import { NextResponse, type NextRequest } from "next/server"

import {
  REFERRAL_CODE,
  REFERRAL_COOKIE,
  REFERRAL_DAYS,
  REFERRAL_PARAM,
} from "@/constants/referral"
import { contentSecurityPolicy } from "@/lib/csp"

/** A fresh nonce for every page; Next.js adds it to its own scripts from the request header. */
export function proxy(request: NextRequest) {
  const nonce = Buffer.from(crypto.randomUUID()).toString("base64")
  const policy = contentSecurityPolicy(
    nonce,
    process.env.NODE_ENV === "development"
  )
  const requestHeaders = new Headers(request.headers)
  requestHeaders.set("x-nonce", nonce)
  requestHeaders.set("Content-Security-Policy", policy)

  const response = NextResponse.next({ request: { headers: requestHeaders } })
  response.headers.set("Content-Security-Policy", policy)

  // A referral link: kept until the visitor signs up or makes a company, where it counts.
  const referral = request.nextUrl.searchParams.get(REFERRAL_PARAM)

  if (referral && REFERRAL_CODE.test(referral)) {
    response.cookies.set(REFERRAL_COOKIE, referral, {
      maxAge: REFERRAL_DAYS * 24 * 60 * 60,
      sameSite: "lax",
      httpOnly: true,
      secure: request.nextUrl.protocol === "https:",
      path: "/",
    })
  }

  return response
}

// Pages only: not the API, static files or link prefetches.
export const config = {
  matcher: [
    {
      source: "/((?!api|_next/static|_next/image|favicon.ico|icon.svg).*)",
      missing: [
        { type: "header", key: "next-router-prefetch" },
        { type: "header", key: "purpose", value: "prefetch" },
      ],
    },
  ],
}
