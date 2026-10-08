# prepza.

⭐ Like it? Star it. ⭐ Helps a looooooot

Timed knowledge interviews for hiring, made from a job description or a ready-made template. A company pastes the role, reviews the topics, and invites candidates; each candidate gets their own random questions with a countdown on every one, and the company sees their scores and integrity signals. People preparing for a role practise free on the templates. Any role, 23 languages, from $1 per candidate.

**For private and research use only.** This repository may not be used for commercial purposes. See [LICENSE.md](LICENSE.md) (PolyForm Noncommercial 1.0.0).

![prepza](screenshot.png)

## Features

- **Interviews from a job description:** the AI proposes topics, the company reviews them for free, then each topic gets a bank of multiple-choice questions.
- **Ready-made templates:** copy an interview by role, level and language at once, for free.
- **Timed and fair:** each candidate gets their own random questions, with a server-enforced countdown on every one.
- **Scorecards and reports:** grades against a pass mark, integrity flags, and PDF reports to download, email or share.
- **Invites three ways:** by email, from a list or file, or through one shareable link for a job ad.
- **Teams and verified companies:** owners, admins and viewers; a check next to a verified company's name.
- **Questions that fix themselves:** answers, votes and reports flag weak questions, and a verifier fixes them.
- **ATS integrations:** candidates from Workable, Greenhouse, Teamtailor, Recruitee and Breezy HR are invited automatically, and results go back.
- **Slack:** a company picks a channel and which of its notifications go there.
- **Public API:** API keys to list interviews, invite candidates and read results, and a signed web hook when a candidate finishes; its reference is on the site.
- **Pay per candidate:** credits that never expire, $1–3 per candidate, with no paid subscription (an optional automatic top-up saves the card with Paddle as a $0 subscription).
- **Free practice:** people preparing for a role practise on the templates' revealed questions.
- **23 languages:** the interface, generated interviews, emails and news posts.
- **News:** a public news page; posts are written in English in the admin zone and translated automatically.
- **Admin zone:** templates, news, question quality, verification, pass rates, stats, and the pause and maintenance switches.

## Quick start

Requirements: Docker with Compose, and an OpenAI API key.

```bash
cp .env.example .env
# Set OPENAI_API_KEY in .env.
docker compose up --build
```

Then open the app at http://localhost:8090. Sign-in uses the Firebase Auth emulator (http://localhost:4100), and every email lands in Mailpit (http://localhost:8125). More in [Development](docs/development.md).

## Documentation

### Product

| Page | What it covers |
|---|---|
| [Companies](docs/features/companies.md) | Company names, the team and its roles, logos, verification |
| [Interviews](docs/features/interviews.md) | Making an interview, topic review, the interview page and its settings, preview |
| [Candidates](docs/features/candidates.md) | Invites, the shareable link, taking an interview, timing, scorecards, reports |
| [Templates and practice](docs/features/templates-and-practice.md) | The question bank, copying templates, slugs, free practice |
| [Credits and payments](docs/features/billing.md) | Credits, top-ups, automatic top-up, referrals, setting up Paddle |
| [ATS integrations](docs/features/ats.md) | Connecting Workable, Greenhouse, Teamtailor, Recruitee and Breezy HR, linked jobs, results back to the ATS |
| [Public API](docs/features/api.md) | API keys and their expiry, the routes, signed web hooks, the API page and docs |
| [Notifications and emails](docs/features/notifications.md) | The bell, emails, Slack, setting up Resend and Slack |
| [In-app assistant](docs/features/assistant.md) | Answers about a user's companies and about prepza, its limits, retention and tools |
| [Admin zone](docs/features/admin-zone.md) | Superadmins' templates, news, quality, pass rates, stats, pause and maintenance mode |
| [Public site](docs/features/site.md) | Home page, skills tests, articles, FAQ and help chat, legal pages, contact, SEO |
| [Languages](docs/features/languages.md) | The 23 languages, language addresses, fonts, right-to-left |

### Engineering

| Page | What it covers |
|---|---|
| [Architecture](docs/architecture.md) | Services, how they call each other, background jobs, events and Pub/Sub |
| [Generation and question quality](docs/generation.md) | The generation pipeline, question reuse and checks, generation settings, models, rate limits |
| [Development](docs/development.md) | Running locally, settings, the local stack, everyday commands, conventions |
| [Testing](docs/testing.md) | Unit, integration, browser, end-to-end and load tests; CI |
| [Deployment](docs/deployment.md) | Production images, migrations, Sentry, CI/CD, releases and rollbacks |
| [infra/README.md](infra/README.md) | Google Cloud with Terraform: bootstrap, deploys, restore drill |
| [packages/common](packages/common/README.md) | The code the API services share |
| [e2e_tests/load/README.md](e2e_tests/load/README.md) | Load test settings, thresholds and results |
| [evals/README.md](evals/README.md) | Offline evals of models and prompts |

## Project conventions

See [CLAUDE.md](CLAUDE.md): separate modules for schemas, models, prompts, helpers and constants; `app/main.py` only wires the app; at most 300 lines per file; the simplest solution that works; and no business logic on the frontend (rules, thresholds and decisions live in the services).
