# Public site

The pages anyone can open without signing in, and how search engines see them. Every public page also has an address in each language (see [Languages](languages.md#language-addresses)).

- [Home page](#home-page)
- [Skills tests by role](#skills-tests-by-role)
- [Articles](#articles)
- [FAQ and help chat](#faq-and-help-chat)
- [Legal pages](#legal-pages)
- [Documents for companies](#documents-for-companies)
- [Contact us](#contact-us)
- [About us and the footer](#about-us-and-the-footer)
- [Search engines](#search-engines)

## Home page

The first screen: "Test everyone. Hire the best." and the box to paste a job description. Submitting it:

1. signs you in if needed,
2. asks which company the interview is for (or its name, for a first company),
3. starts the generation.

Below, a landing page walks through prepza, one section per screen:

- how it works,
- why prepza: six advantages at a glance (ready in minutes, any role, harder to cheat, no subscription, ranked results, 23 languages),
- seeing who knows the job,
- trying it before your candidates do (free templates and a preview),
- sharing results,
- topic review,
- questions that fix themselves,
- one link for a job ad,
- the ATS integrations: Workable, Greenhouse, Teamtailor, Recruitee and Breezy HR, with their logos,
- a verified brand,
- languages,
- pricing ("$1–3 per candidate, with no subscription"),
- a closing call to action.

Each section has a picture of the real interface, several of them animated. Prices come from billing, so they follow any change. Signed-in users see the landing page too.

## Skills tests by role

`/tests` and `/tests/<slug>`: a page per template, for companies hiring for the role. It shows:

- what the test covers,
- the way to create a test,
- up to 5 of its revealed questions with answers as examples, and a link to free practice,
- "questions companies ask": the FAQ's answers on cost, charging, cheating, what candidates see and languages. It has no FAQ structured data; `/faq` carries that.

Addresses use the template's slug (see [Templates and practice](templates-and-practice.md#slugs)); an old address by id moves there for good.

A role page, like the template's free practice page, is in English and in its template's language only. For a German template, that's `/de/tests/<slug>` and `/de/practice/<slug>`, with hreflang between the two. Its address in any other language isn't found.

## Articles

The articles are `/pre-employment-testing`, `/ai-interviews`, `/compare` and its pages, and `/guides` and its pages.

- They are Markdown in `frontend/content/` (`pages/`, `compare/`, `guides/`).
- Each has a short frontmatter: `title`, `seoTitle`, `description`, `updated`.
- `lib/content.ts` and `components/content/` show them.
- A new file is a new page, in its hub and the sitemap.

**Translations** live in `content/<language>/<folder>/`, under the same file name.

- A page shows its translation in the interface's language.
- Where there is none, it shows English, with a note.
- It names only its real translations, for hreflang and in the sitemap.

**Comparisons** name no competitor prices and say where each tool fits better; prepza is presented as complementary.

## FAQ and help chat

`/faq` has the common questions, in the interface language, with today's prices. At the end is an AI help chat about prepza, open to visitors too.

- It answers only from the platform guide, the FAQ, the prices, the terms and the privacy policy.
- It answers in the page's language.
- Nothing of the conversation is stored.

| Limit | Setting | Value |
|---|---|---|
| Messages an hour per account | `HELP_USER_LIMIT` | 30 |
| Questions an hour per address | `HELP_IP_LIMIT` | 60 |
| Questions a day in all | `HELP_DAILY_LIMIT` | 5,000 |
| Questions per 10 minutes per IP, at the edge (Google Cloud only) | — | 20 |

The chat's model is set in [Generation settings](../generation.md#models).

## Legal pages

- The privacy policy and terms are served by the rounds service, in English only. The help chat answers from them too.
- The contact address in them, hello@prepza.ai, is put together in the browser, so the page's HTML doesn't hold it for bots to collect.

## Documents for companies

The `/documents` page ("docs" in the footer) offers companies:

- instructions for use, as a PDF,
- the data processing agreement, as a PDF,
- candidate notice and DPIA templates, as editable Word files.

Their sources are the Markdown files in `frontend/content/documents`, in English only, like the legal pages. The DPA's text must match `services/rounds/app/constants/dpa.py`.

After changing one, rebuild the files in `frontend/public/documents` and commit them:

```bash
./scripts/documents/build.sh   # needs uv (for pandoc) and Docker (Chromium prints the PDFs)
```

## Contact us

`/contact` is a form with a name, an email and a message.

- The message is emailed to hello@prepza.ai (`CONTACT_EMAIL` in notifications).
- The visitor's address is the reply-to, so answering the email answers them.
- At most 5 messages a day per address (`CONTACT_IP_LIMIT`).
- At most 200 a day in all (`CONTACT_DAILY_LIMIT`).

## About us and the footer

`/about` explains why prepza exists for companies, free practice for people preparing, and its solo founder.

The footer links free practice, pricing, the privacy policy, the terms, the FAQ, About us and Contact us.

## Search engines

Every public page has its title, description, canonical address and link-preview image.

**Link-preview images:**

- The logo over the page's own title in its language, drawn by `app/preview/route.tsx` in the site's dark theme and Poppins (`frontend/assets/fonts`). Other scripts' letters come from Google Fonts.
- The home page uses the home page's promise instead (`app/opengraph-image.tsx`). So do Arabic, Persian, Hebrew and Hindi, which the renderer can't draw.

**Structured data:** organization, product and price range, founder, articles, breadcrumbs, FAQ.

**Sitemap:** every language version, template page and article.

**Indexing:**

- Private pages (signed-in areas and personal links) answer with `X-Robots-Tag: noindex`.
- robots.txt blocks only `/api/` and `/monitoring`.
- `GOOGLE_SITE_VERIFICATION` and `BING_SITE_VERIFICATION` add Search Console's and Bing's ownership tags when set.
