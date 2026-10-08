# Companies

A company is where a hiring team works: its interviews, candidates, credits and team live under it. Companies' pages live under `/companies`; old `/company` links redirect.

## Names

- Company names are unique across prepza, ignoring case.
- A company can be renamed.
- One person can own at most 3 companies.

## Team

A company has one owner. On the company's **Team** tab, the owner adds a member's email with a role, **admin** or **viewer**, and copies the join link that appears; no email is sent, so the owner passes the link on. Only someone signed in with that email can accept it, so a forwarded link is useless to anyone else. The owner can change a member's role later, and remove a member or withdraw a pending invite.

| Role | What they can do |
|---|---|
| Owner | Everything, including managing the team and removing the company |
| Admin | Works like the owner, except managing the team and removing the company |
| Viewer | Sees the company's interviews, questions, candidates and scorecards; downloads and shares reports; previews interviews. Changes nothing and spends no credits |

The companies service enforces the roles: `require_editor` answers 403 to a viewer.

## Logo

A company can upload its logo: PNG, JPEG or WebP, up to 500 KB. It is shown on:

- invite emails,
- the interview candidates take,
- PDF reports.

## Verification

A verified company has a check next to its name everywhere.

1. An owner or admin gives the company's website.
2. They prove its domain by signing in with a verified email on it. Free mail services don't count.
3. The company waits for a superadmin's review on the admin zone's **Verification** tab. Meanwhile a clock shows next to its name, for its members only.

The decision:

- **Approved:** a check shows next to its name everywhere.
- **Declined:** its owners and admins see why. It goes for review again only after its name or website changes.
- Both decisions reach the owners and admins in the bell.

Later changes:

- Renaming a verified, pending or declined company sends the new name for review, taking any check away.
- Changing the website starts over.

## Audit log

The companies service records the human decisions taken in a company, as evidence of human oversight: who took each one, what it was, on which interview or candidate, and when.

| Recorded | When |
|---|---|
| Topics approved | A member approves an interview's topics |
| Results viewed | A member opens a candidate's results |
| Report emailed | A member emails a candidate's or an interview's report |
| Candidate deleted / invite revoked | A member revokes a candidate (see [Candidates](candidates.md#revoking-a-candidate)) |
| Extra time set | A member gives a candidate extra time |
| Pass mark changed | A member changes an interview's pass mark |

Only the owner can read the log, newest first, through `GET /companies/{id}/audit`; the app has no page for it. Events are kept for 24 months, then the daily retention job deletes them, and they go with the company when it's removed. When a member deletes their account, their events stay with the company without their id (`deleted-user`); their data export lists them.

## Related pages

- [Interviews](interviews.md): making and running a company's interviews.
- [Candidates](candidates.md): invites, scorecards and reports.
- [Credits and payments](billing.md): the company's wallet and referrals.
- [ATS integrations](ats.md): connecting Workable, Greenhouse, Teamtailor, Recruitee or Breezy HR.
- [Notifications and emails](notifications.md#slack): a company's notifications in Slack.
- [Public API](api.md): API keys and web hooks for a company's own platform.
