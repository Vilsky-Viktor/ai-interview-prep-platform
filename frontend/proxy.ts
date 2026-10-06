import { NextResponse, type NextRequest } from "next/server"

import {
  REFERRAL_CODE,
  REFERRAL_COOKIE,
  REFERRAL_DAYS,
  REFERRAL_PARAM,
} from "@/constants/referral"
import { TOKEN_COOKIE } from "@/constants/auth"
import { MAINTENANCE_HEADER } from "@/constants/maintenance"
import { contentSecurityPolicy } from "@/lib/csp"
import { maintenanceState } from "@/lib/maintenance"

/** A fresh nonce for every page; Next.js adds it to its own scripts from the request header.
 * While maintenance mode is on, every page is the maintenance screen, except for superadmins. */
export async function proxy(request: NextRequest) {
  const nonce = Buffer.from(crypto.randomUUID()).toString("base64")
  const policy = contentSecurityPolicy(
    nonce,
    process.env.NODE_ENV === "development"
  )
  const requestHeaders = new Headers(request.headers)
  requestHeaders.set("x-nonce", nonce)
  requestHeaders.set("Content-Security-Policy", policy)

  const maintenance = await maintenanceState(
    request.cookies.get(TOKEN_COOKIE)?.value
  )
  requestHeaders.set(MAINTENANCE_HEADER, maintenance)

  const response =
    maintenance === "closed"
      ? NextResponse.rewrite(new URL("/maintenance", request.url), {
          status: 503,
          request: { headers: requestHeaders },
        })
      : NextResponse.next({ request: { headers: requestHeaders } })
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
