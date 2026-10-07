// The token cookie the frontend writes once signed in (frontend/constants/auth.ts).
export const TOKEN_COOKIE = "prepza_token"
// Screenshots, one folder per spec, in the results folder Playwright empties at the start of a run;
// git ignores it.
export const SCREENSHOTS = "test-results/screenshots"
// The shortest time per question the API allows (services/companies/app/constants/interviews.py).
export const MIN_QUESTION_SECONDS = 10
// The companies database, for the invite links candidates are emailed (like e2e.py).
export const POSTGRES_HOST = "postgres"
// The API as the test process reaches it: the gateway on the stack's network (signed-in.sh).
export const API_URL = process.env.API_URL ?? "http://gateway/api"
// The site as the test process reaches it, for warming up the dev server's pages.
export const FRONTEND_URL = process.env.FRONTEND_URL ?? "http://gateway"
const SOME_ID = "00000000-0000-0000-0000-000000000000"
// Every page the specs open, so each is compiled before the browser starts (warm-up.ts).
export const WARM_UP_PATHS = [
  "/",
  "/companies",
  `/companies/${SOME_ID}/interviews`,
  `/companies/${SOME_ID}/interviews/new`,
  `/companies/${SOME_ID}/interviews/${SOME_ID}`,
  `/companies/${SOME_ID}/templates`,
  `/companies/${SOME_ID}/members`,
  `/invite/${SOME_ID}`,
  `/join/${SOME_ID}`,
  `/sessions/${SOME_ID}`,
  "/maintenance",
  "/superadmin/pass-rates",
  "/superadmin/verification",
  "/superadmin/controls",
]

// The web hook secret key of the Greenhouse connection the tests save.
export const GREENHOUSE_E2E_SECRET = "e2e-webhook-secret"
