import { expect, test } from "../fixtures"
import { api, createCompany, templatesBySize } from "../helpers/api"
import { visit } from "../helpers/navigation"
import { shot } from "../helpers/screenshots"
import { randomId, throwawayEmail } from "../helpers/users"

// From free practice to hiring: a practice result offers the same test for the user's own
// candidates, in a company they choose: a new one, their only one, or one of several.
test("a practice result leads to using its test in a company", async ({ signInAs }) => {
  const user = await signInAs(throwawayEmail("practice-hire"))
  // A template companies can use, as in CI's seed; a third of its questions are for practice.
  const [template] = await templatesBySize(user)
  const picker = `/companies/templates/${template.id}`
  const opensTemplate = new RegExp(`/companies/[^/]+/templates/${template.id}$`)

  // The result screen, even before the round is finished, offers the test for hiring.
  const round = await api<{ round_id: string }>(user, "POST", `/rounds/practice/${template.id}`)
  await visit(user, `/practice/rounds/${round.round_id}`)
  await expect(user.getByText("Hiring for this role?")).toBeVisible()
  await shot(user, "result-hire")

  // No company yet: the choice is empty, and a new company opens on the test.
  await user.getByRole("button", { name: "Create interview" }).click()
  await user.waitForURL(new RegExp(`${picker}$`))
  await expect(user.getByRole("heading", { name: "Choose a company" })).toBeVisible()
  await expect(user.getByText("No companies yet.")).toBeVisible()
  await shot(user, "pick-none")
  await user.getByRole("button", { name: "New company" }).click()
  await user.getByLabel("Company name").fill(`E2E ${randomId()}`)
  await user.getByRole("button", { name: "Create", exact: true }).click()
  await user.waitForURL(opensTemplate)
  await expect(user.getByRole("button", { name: "Use template" })).toBeVisible()

  // One company: straight to the test in it.
  await visit(user, picker)
  await user.waitForURL(opensTemplate)

  // Several: each row opens the test in its company, with nothing to remove here.
  const second = await createCompany(user)
  await visit(user, picker)
  const row = user.getByRole("link", { name: new RegExp(second.name) })
  await expect(row).toHaveAttribute("href", `/companies/${second.id}/templates/${template.id}`)
  await expect(user.getByRole("button", { name: "Remove" })).toHaveCount(0)
  await shot(user, "pick-several")
})

// A finished practice lists its questions by topic, without numbers.
test("a finished practice lists its questions without numbers", async ({ signInAs }) => {
  const user = await signInAs(throwawayEmail("practice-review"))
  const [template] = await templatesBySize(user)
  const round = await api<{ round_id: string }>(user, "POST", `/rounds/practice/${template.id}`)
  const result = await api<{ topics: { session_id: string }[] }>(
    user,
    "GET",
    `/rounds/practice/rounds/${round.round_id}`
  )

  for (const topic of result.topics) {
    await api(user, "POST", `/rounds/sessions/${topic.session_id}/finish`)
  }

  await visit(user, `/practice/rounds/${round.round_id}`)
  await expect(user.getByText("Good question?").first()).toBeVisible()
  await expect(user.getByText(/^\d+\.$/)).toHaveCount(0)
  await shot(user, "practice-review")
})
