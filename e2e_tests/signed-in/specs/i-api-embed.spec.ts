import { expect, test } from "../fixtures"
import { API_URL, FRONTEND_URL } from "../constants"
import { api, createCompany, createInterview } from "../helpers/api"
import { shot } from "../helpers/screenshots"
import { ownerEmail, throwawayEmail } from "../helpers/users"

// The company's own site, at an address of its website's domain: it embeds the interview with
// the hosted script and hears when the candidate has finished.
const DOMAIN = "acme-embed.com"
const SITE = `http://jobs.${DOMAIN}`

function sitePage(siteUrl: string, inviteUrl: string) {
  return `<!doctype html><html><head><title>Acme careers</title></head><body>
    <h1>Acme careers</h1><div id="interview"></div>
    <script src="${siteUrl}/embed/v1.js"></script>
    <script>
      window.events = []
      Prepza.embed({
        element: "#interview",
        url: ${JSON.stringify(inviteUrl)},
        onReady: () => window.events.push("ready"),
        onStart: () => window.events.push("started"),
        onFinish: ({ candidateId }) => window.events.push("finished:" + candidateId),
      })
    </script></body></html>`
}

test("a company's own site embeds a candidate's interview and hears it finish", async ({
  browser,
  baseURL,
  signInAs,
}) => {
  const owner = await signInAs(ownerEmail())
  const company = await createCompany(owner)
  const interviewId = await createInterview(owner, company.id)
  await api(owner, "PUT", `/companies/companies/${company.id}/website`, {
    website: DOMAIN,
  })
  const { key } = await api<{ key: string }>(
    owner,
    "POST",
    `/v1/manage/keys?company_id=${company.id}`,
    { name: "Careers site", expiry: "1" }
  )
  const invite = async (email: string, signIn: boolean) => {
    const response = await owner.request.post(
      `${API_URL}/v1/interviews/${interviewId}/candidates`,
      { headers: { Authorization: `Bearer ${key}` }, data: { email, sign_in: signIn } }
    )
    expect(response.status()).toBe(201)

    return (await response.json()) as { id: string; invite_url: string }
  }
  const framers = async (inviteUrl: string) => {
    const token = new URL(inviteUrl).pathname.split("/").pop()
    const page = await owner.request.get(`${FRONTEND_URL}/embedded/${token}`)

    return page.headers()["content-security-policy"].match(/frame-ancestors ([^;]+)/)?.[1]
  }

  const candidate = await invite(throwawayEmail("embedded"), false)
  // Only the company's own site may frame it; an invite by email, no site.
  expect(await framers(candidate.invite_url)).toBe(`${DOMAIN} *.${DOMAIN}`)
  const byEmail = await invite(throwawayEmail("by-email"), true)
  expect(await framers(byEmail.invite_url)).toBe("'none'")

  const context = await browser.newContext()
  const site = await context.newPage()
  await site.route(`${SITE}/**`, (route) =>
    route.fulfill({ contentType: "text/html", body: sitePage(baseURL!, candidate.invite_url) })
  )
  await site.goto(`${SITE}/apply`)
  const frame = site.frameLocator("iframe")

  // No sign-in, no prepza header or footer: the invitation, then the questions in place.
  await expect(frame.getByRole("button", { name: "Accept & Start" })).toBeVisible()
  await expect(frame.locator("header, footer")).toHaveCount(0)
  await shot(site, "invitation")
  await frame.getByRole("button", { name: "Accept & Start" }).click()
  await expect(frame.getByRole("button", { name: "Finish interview" })).toBeVisible({
    timeout: 60_000,
  })
  await expect(frame.locator("header, footer")).toHaveCount(0)
  await shot(site, "question")
  await frame.getByRole("button", { name: "Finish interview" }).click()
  await frame.getByRole("dialog").getByRole("button", { name: "Finish", exact: true }).click()
  await expect(frame.getByText("You have finished the interview. Good luck!")).toBeVisible()
  await expect(frame.getByRole("button", { name: /Back to/ })).toHaveCount(0)
  await expect
    .poll(() => site.evaluate(() => (window as unknown as { events: string[] }).events))
    .toEqual(["ready", "started", `finished:${candidate.id}`])
  await shot(site, "finished")
  await context.close()
})
