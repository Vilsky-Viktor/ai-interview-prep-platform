# Companies

A company is where a hiring team works: its interviews, candidates, credits and team live under it. Companies' pages live under `/companies`; old `/company` links redirect.

## Names

- Company names are unique across prepza, ignoring case.
- A company can be renamed.
- One person can own at most 3 companies.

## Team

A company has one owner. On the company's **Team** tab, the owner adds a member's email with a role, **admin** or **viewer**, and the member is emailed the join link, in the owner's language and with the company's logo; the link also appears on the tab, to copy and pass on if the email doesn't arrive. The invite counts toward the owner's email limits. A company holds at most 20 invites not yet accepted (`MAX_PENDING_INVITES`), and one that never topped up sends at most 10 a day (`MEMBER_INVITES_PER_UNPAID_DAY`), so invites can't be used to email strangers from prepza's domain. A visitor who isn't signed in sees the invitation (the company, not the invited email) with a **Sign in to join** button. When the member joins, the owner gets a [bell notification](notifications.md#what-gets-a-notification). A used link stays readable: the member who joined sees "You've joined" with **Open company**, anyone else "This invite has already been used"; joining again, even twice at the same moment, changes nothing and tells the owner once. An invite withdrawn meanwhile is not found (404), and the same email invited twice at once is refused the second time (409). Only someone signed in with that email can accept it, so a forwarded link is useless to anyone else. The owner can change a member's role later, and remove a member or withdraw a pending invite.

| Role | What they can do |
|---|---|
| Owner | Everything, including managing the team and removing the company |
| Admin | Works like the owner, except managing the team and removing the company |
| Viewer | Sees the company's interviews, questions, candidates and scorecards; downloads and shares reports; previews interviews. Changes nothing and spends no credits |

The companies service enforces the roles: `require_editor` answers 403 to a viewer.

### Handing the company on

The owner can make an admin who has joined the owner: the role picker on that admin's row has an **owner** choice (`can_own` in the team list says who), which asks to confirm first (`POST /companies/members/{id}/owner`). In one transaction the admin becomes the owner and the owner an admin, only while both are still what was read, so a company never has two owners or none. Someone who already owns 3 companies can't become an owner of another (409). The new owner gets a bell notification (`ownership_received`), and the audit log records it (`ownership_transferred`). An automatic top-up keeps charging the card of whoever set it up. It isn't one of the assistant's or AI apps' tools.

### Deleting an account that owns companies

The delete-account dialog asks companies what deleting the account does to the companies the user owns (`GET /companies/account/deletion`): one others have joined blocks it, listed with a link to its team, until another member is made its owner or the company is deleted; one only the user is in is deleted with the account, listed with its credits. Companies also refuses the deletion itself (409) while the user owns a company others joined; library asks companies first, so nothing is deleted then.

## Brand

A company's **brand** tab (owners and admins, like billing) sets how its candidates see the whole interview process: the invitation, the shared test link, the questions, the finished page, the embedded interview and a member's preview. Those pages never show prepza's header or footer, only the company.

### Logo

A company can upload its logo: PNG, JPEG or WebP, up to 500 KB, on the brand tab or by clicking the logo beside its name (hovering an editable logo shows an edit icon in its middle). It is shown on:

- invite and reminder emails, beside the title,
- the invite page and the interview candidates take, above the title on the finished screen,
- PDF reports.

### Font and corners

After the colors: the font (by default prepza's pair, Poppins titles over Geist text; or one font for all the text, one of the most used web fonts: Inter, Roboto, Open Sans, Lato, Montserrat, Nunito, Raleway, Work Sans, Source Sans 3, Noto Sans, PT Sans, Ubuntu, Rubik, Manrope, DM Sans, IBM Plex Sans, Mulish, Fira Sans, Plus Jakarta Sans, Outfit, Merriweather, Lora and Playfair Display), and how round the corners are, 0–24 px: the cards' (10 by default) and the buttons' (24 by default: prepza's pills, half a 48 px button's height). Both are the same in the light and dark themes (`PUT /companies/{id}/brand-style`, `brand_font`, `brand_radius`, `brand_button_radius`). The site bundles each font (`constants/brand-fonts.ts`, not preloaded): a page downloads only the one it uses, each falling back to Geist for letters it lacks.

### Colors

Two sets, one for the light theme and one for the dark, each in groups like a theme's: **page** (background, text), **primary** (buttons, the picked answer's outline, the timer, links; and the text on buttons), **secondary** (fills such as the rules box and the picked answer; the gray text), **dialogs** (background, text) and **borders**. Each starts from prepza's own (`PREPZA_COLORS`) and is saved on its own (`PUT /companies/{id}/brand-colors/{light|dark}`, merged in SQL into `brand_colors`, so two people saving the two themes keep both). Every text must read on its background at WCAG AA's 4.5:1 and the buttons on the page at 3:1, or saving is refused with the group to fix (`helpers/brand.py`), so no candidate is tested on a page they can't read. **Save** keeps what's on screen: the theme's colors, the font and the rounding. **Reset** brings back what was last saved; **reset to prepza defaults**, shown while anything saved isn't prepza's, goes back to prepza's colors in both themes, font and rounding (`GET /brand/prepza` gives them). A live preview (a sample HR question about branding, the start button and the finish dialog) shows the set being edited.

Which theme a candidate sees: the one the address asks for (`?theme=light`, `dark` or `default`, which the SDK passes), else the one the invite asked for through the API (`theme`), else the candidate's own light or dark setting. The candidate's pages set the theme variables of that set on the page (`hooks/use-brand-colors.ts`); without a set of its own, a theme is prepza's.

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

Until a company is verified, its invite pages and its invite and reminder emails say, in a small gray line, that prepza hasn't verified it.

## Suspension

A superadmin can suspend a company from the admin zone (see [Admin zone](admin-zone.md#companies)), and lift the suspension later. While it's suspended:

- its members still see it, with a notice saying so, but nothing in it can be changed,
- it invites nobody: new candidates are refused (an ATS keeps them waiting until the suspension is lifted),
- candidates who haven't started find its invites and shareable link invalid; those already in an interview can finish it.

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
| Ownership transferred | The owner makes an admin the owner |
| AI apps allowed or stopped | An owner or admin changes **Allow AI apps** (see [AI apps](mcp.md#tools)) |

An event also says what it came through (`via`): empty when a member acted in the app, `assistant` when the in-app assistant did it for them, and `mcp` when an AI app connected over MCP did, for every event: results viewed, topics approved, the pass mark changed, a candidate revoked or removed, extra time set and a report emailed. Companies trusts that only from a service token the assistant signs (the `X-Assistant` header, checked like other service calls); a missing or invalid one counts as the app. A view through the assistant isn't counted as the "results viewed" step of the sign-up funnel.

Only the owner can read the log, newest first, with `via`, through `GET /companies/{id}/audit`; the app has no page for it. Events are kept for 24 months, then the daily retention job deletes them, and they go with the company when it's removed. When a member deletes their account, their events stay with the company without their id (`deleted-user`); their data export lists them.

## Page guides

Every page from the companies list inward has an info button (a question mark in a badge, labelled "About this page"): under the back arrow in the page margin, or right after the arrow on narrower screens. It opens a short guide to that page: what it's for, what you can do there and a tip or two. The companies list, each company tab (interviews, templates, team, integrations, brand, billing, referrals), each interview tab (topics, candidates, settings), a new interview and its topic review and generation, the preview, a candidate's report, a template, choosing a company for a template, and the ATS, Slack and API pages each have their own, in every language. The companies list's back arrow goes to the home page.

## Related pages

- [Interviews](interviews.md): making and running a company's interviews.
- [Candidates](candidates.md): invites, scorecards and reports.
- [Credits and payments](billing.md): the company's wallet and referrals.
- [ATS integrations](ats.md): connecting Workable, Greenhouse, Teamtailor, Recruitee or Breezy HR.
- [Notifications and emails](notifications.md#slack): a company's notifications in Slack.
- [Public API](api.md): API keys and web hooks for a company's own platform.
