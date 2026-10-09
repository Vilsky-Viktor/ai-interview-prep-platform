# Public site

The pages anyone can open without signing in, and how search engines see them. Every public page also has an address in each language (see [Languages](languages.md#language-addresses)).

- [Home page](#home-page)
- [Skills tests by role](#skills-tests-by-role)
- [Articles](#articles)
- [FAQ and help chat](#faq-and-help-chat)
- [Legal pages](#legal-pages)
- [Documents for companies](#documents-for-companies)
- [Contact us](#contact-us)
- [News](#news)
- [About us and the footer](#about-us-and-the-footer)
- [Search engines](#search-engines)

## Home page

The first screen: "Test everyone. Hire the best.", a "Demos" button with a play icon beside it (under the text on phones) to prepza's YouTube channel, with an info button next to it that explains in a dialog how prepza works (the steps and the price per candidate), and the box to paste a job description. Submitting it:

1. signs you in if needed,
2. asks which company the interview is for (or its name, for a first company),
3. starts the generation.

Below, a landing page walks through prepza, one section per screen:

- how it works,
- why prepza: six advantages at a glance (ready in minutes, any role, harder to cheat, no subscription, ranked results, 23 languages),
- seeing who knows the job,
- trying it before your candidates do (free templates and a preview),
- four ways to invite candidates: by email, from a list or file, a shareable link for a job ad, and from an ATS,
- sharing results,
- topic review,
- questions that fix themselves,
- the tools prepza works with: the ATSs (Workable, Greenhouse, Teamtailor, Recruitee, Breezy HR) and Slack as their logos, and the API as an example request with a link to its docs,
- a verified brand,
- fair to candidates and safe for your data: what's true about human review, answer keys, AI training, extra time, candidate notices and data, data retention and hosting, payments and the documents, with links to the documents, terms and privacy policy (no compliance badges),
- pricing ("Pay per candidate": interviews and the first candidates free, then a price per candidate, with no subscription),
- a closing call to action: "Create an interview", then the demos and the FAQ ("Demos" with "Go to FAQ" beside it).

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

`/faq` has the common questions, in the interface language, with today's prices; its intro points to the assistant ("ask agent" in the header) for anything else.

The help chat (rounds' `POST /help/chat`) answers signed-out visitors in the [assistant's panel](assistant.md#the-panel):

- It answers only from the platform guide, the FAQ, the prices, the terms and the privacy policy, and keeps to prepza and hiring with it, like the assistant (`prepza_common.scope.SCOPE_RULE`).
- It answers in the page's language.
- Nothing of the conversation is stored: the panel sends it whole each time.
- A conversation with a secret in it (a key, a token, a password) is answered at once with a fixed reply, before the limits or the model, and nothing of it is used; see [the assistant's secrets](assistant.md#secrets-pasted-into-the-chat).
- A visitor asking to sign in or sign up, or to do something that needs an account (create a company, …), gets a sign-in card in the panel (the site's own sign-in buttons, the way they named first): the model starts its reply with a `[[sign_in:<provider>]]` marker, which the service turns into a `{"block": {"kind": "sign_in", "provider"}}` event.
- The same knowledge, with the FAQ in the page's language, is served as text at `GET /api/rounds/help/guide` (public, kept for 5 minutes per language); the in-app assistant reads it to answer questions about prepza.

| Limit | Where it's set | Value |
|---|---|---|
| Messages an hour per account | `HELP_USER_LIMIT` setting | 30 |
| Questions an hour per address | `HELP_IP_LIMIT` constant (`services/rounds/app/constants/help.py`) | 60 |
| Questions a day in all | `HELP_DAILY_LIMIT` setting | 5,000 |
| Questions per 10 minutes per IP, at the edge (Google Cloud only) | Cloud Armor (Terraform) | 20 |

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

## API docs

The `/api-docs` page ("api docs" in the footer) is the public API's reference, in English only, like the legal pages. It reads the API's OpenAPI description on each request (`lib/openapi.ts`, `components/api-docs/`): its description's sections (getting a key, authentication, limits, errors, web hooks), the base URL, each route with its parameters, body, result and errors, the `candidate.finished` and `candidate.rescored` web hooks and the objects. See [Public API](api.md).

## Contact us

`/contact` is a form with a name, an email and a message.

- The message is emailed to hello@prepza.ai (`CONTACT_EMAIL` in notifications).
- The visitor's address is the reply-to, so answering the email answers them.
- At most 5 messages a day per address (the `CONTACT_IP_LIMIT` constant in `services/rounds/app/constants/contact.py`).
- At most 200 a day in all (the `CONTACT_DAILY_LIMIT` setting).

## News

`/news` ("prepza news.") lists prepza's posts newest first, one after another: title (ending with the blue dot, like the site's headings), date and text. No pictures, links or detail pages; the text is plain, with its line breaks. Superadmins write them in the [admin zone](admin-zone.md#news).

- Posts are written in English and translated into every other language after they're saved. Each language's page (`/de/news`, …) shows its translation, or the English post while there's none.
- The first page is rendered on the server; the next loads when you scroll near the end (library's public `GET /news?offset=&limit=`, in the `Accept-Language` language, no sign-in).
- Posts are read fresh on every request, not through the public data cache, so a new, changed or deleted post shows at once (`lib/news-posts.ts`).
- **Search engines:** its own title and meta description in each language, canonical and hreflang addresses for every language, the link-preview picture, and structured data: a `Blog` with the page's posts as `BlogPosting`s by prepza (`newsData` in `lib/structured-data.ts`). The sitemap lists it in every language, dated by its newest post.
- **RSS:** `/news/rss.xml` (and `/de/news/rss.xml`, … in each language, with the same translations) is an RSS 2.0 feed of the newest 50 posts: each with its title, its text as plain text, its day and its id as the guid, linking to its place on that language's news page (`#<id>`). The page names it in its head and links it with the large RSS icon on the right of its title. It isn't in the sitemap.

## About us and the footer

`/about` explains why prepza exists for companies, free practice for people preparing, and its solo founder.

The footer links, in three columns: skills tests by role and the articles (pre-employment testing, AI interviews, comparisons, guides); the privacy policy, the terms, the documents and the API docs; free practice, the FAQ, About us, News and Contact us. Pricing is in the header's menu, not in the footer.

## Search engines

Every public page has its title, description, canonical address and link-preview image.

**Link-preview images:**

- The logo over the page's own title in its language, drawn by `app/preview/route.tsx` in the site's dark theme and Poppins (`frontend/assets/fonts`). Other scripts' letters come from Google Fonts. The picture is sent with `X-Robots-Tag: noindex`, so search engines don't list it while link-preview bots still fetch it. Each page's picture address carries a signature of its title and language (`PREVIEW_SECRET`), and any other title gets a 404, so nobody can put their own text under the logo.
- The home page uses the home page's promise instead (`app/opengraph-image.tsx`). So do Arabic, Persian, Hebrew and Hindi, which the renderer can't draw.

**Structured data:** organization, product and price range, founder, articles (with their picture and language), the API docs as a technical article in English, breadcrumbs (role and practice pages, the API docs), FAQ (left out when there are no questions).

**Sitemap:** every language version, article, and the pages of each indexable template, dated by the template's last change. The news page is dated by its newest post, and the privacy policy, terms and DPA by their last update.

**Indexing:**

- Private pages (signed-in areas and personal links) answer with `X-Robots-Tag: noindex`.
- A template's role test and practice pages are indexable only when the template has at least 3 topics (`MIN_INDEXABLE_TOPICS`) and is the first template of its title in its language. Others say `noindex` and stay out of the sitemap.
- robots.txt blocks only `/api/` and `/monitoring`.
- `GOOGLE_SITE_VERIFICATION` and `BING_SITE_VERIFICATION` add Search Console's and Bing's ownership tags when set.
