# In-app assistant

Anyone asks the assistant from the "ask agent" button in the header (or at the end of the home page). A signed-in user asks about their companies and about prepza, and gets a streamed answer built from the same pages' data they can already see; a signed-out visitor gets answers about prepza from the FAQ's knowledge. It only reads for now: asking it to change something gets a pointer to the page where it's done (actions, each behind a confirmation, come next). This page describes the panel and the service behind it (`services/assistant`).

- [The panel](#the-panel)
- [What it answers](#what-it-answers)
- [A conversation](#a-conversation)
- [Voice](#voice)
- [Limits](#limits)
- [Roles and privacy](#roles-and-privacy)
- [Retention and deletion](#retention-and-deletion)
- [Tools](#tools)
- [Settings](#settings)

## The panel

- "ask agent" in the header (a pill with a bright arc circling its blue border; the icon alone below `md`) and at the end of the home page open it, with the input ready to type in (not on touch screens, where the keyboard would cover it). It's mounted once for the whole site, so a conversation stays while the user moves between pages, and closing never stops or loses it.
- Wider screens: a drawer at the end side, beside the page, which still scrolls; a click on the page closes it (not one in its own menus and dialogs). Its inner edge drags (or, focused, the arrow keys) to a width between 360px and 900px or 70% of the window, kept per browser. The wheel over it scrolls only its messages.
- Phones: the whole screen, the page behind it doesn't scroll, and following a link closes it.
- Its header: a company picker (signed in), New chat, History (past conversations, opened or deleted after a confirmation) and Close. The picker has the user's companies and "all companies": on a company's pages it starts on that company, elsewhere on all companies, and the user can change it; the pick is kept with the restored chat, and opening a past conversation picks its company. Each message goes with the pick: with a company, the model applies everything to it and never asks which; with all companies, it asks which company for anything that targets one (unless the user named it or has only one), and creating a company needs none.
- A reload brings the panel back as it was: signed in, whether it was open, the conversation it showed (loaded from the service; one that's gone leaves the welcome) and the company pick, in localStorage; signed out, whether it was open and the visitor's messages, in the tab's sessionStorage. New chat forgets the conversation; signing out forgets both. A visitor who signs in keeps their chat on screen, and their first message saves it as the start of a new conversation (`earlier`).
- An empty conversation shows a welcome for where the user is: `GET /welcome?company_id=` decides the stage from what companies shows them (no company, a company not verified, verified without interviews, interviews without candidates, candidates), and the panel shows that stage's text and 3–4 questions to tap (`assistant.welcome` messages). Signed-out visitors get the `signed_out` welcome without a call.
- Each answer is a card (with the tools at work and the dots while it's written, and its error), what its tools found right under it; answers stream in limited markdown (emphasis, lists, code and links to the app's own pages only; no images or HTML); Stop replaces Send while one streams; a failed answer shows its error and Try again; `session_expired` refreshes the token and sends once more.
- Blocks under an answer use the app's own rows: candidates as in an interview's list, interviews as in a company's list, balances as in the company header, and links to the pages the data came from.
- **Signed out** it's the same panel with FAQ answers only: the questions go to rounds' help chat (its limits, nothing stored, see [Public site](site.md#faq-and-help-chat)), with no tools, history, company or voice. Asking to sign in brings a sign-in card; signing in from it keeps the panel open, now signed in.

## What it answers

- **Their data:** companies and roles, balances, referrals, auto top-up, the team, interviews and whether their questions are ready, reports, candidates (in one interview or across a company), one candidate's results, a pause, prices, ATS connections and linked jobs, Slack, API keys and web hooks, notifications, their account, templates.
- **How prepza works:** how-to, pricing, credits, payments, refunds, the terms and the privacy policy, from the platform guide (rounds' `GET /help/guide`, the same knowledge as the help chat signed-out visitors ask), in the user's language.
- Under an answer, the panel shows blocks: candidate rows, interviews, balances, a candidate's summary and links to the pages the data comes from. Links are built only from each tool's link template and ids in the data, never from the model's text.
- Reports are downloaded and shared from their pages: the assistant links to the candidate's or the interview's page.

## A conversation

`POST /api/assistant/chat` with `{conversation_id?, company_id?, message, source?, page?, earlier?}` and the user's ID token. `company_id` is the company picked in the panel (one the user must be able to see), or none for all companies; it's the context of this message, and a new conversation is listed under it. `page` is only context for the model. `earlier` (at most 20 messages, each cut to 2,000 characters) is the chat the user had before signing in, saved at the start of a new conversation and ignored in an existing one. The answer streams as server-sent events:

```
data: {"conversation": {"id": "6f1c…"}}
data: {"tool": {"name": "list_candidates", "state": "running", "label": "Reading candidates…"}}
data: {"tool": {"name": "list_candidates", "state": "done", "label": "Reading candidates…"}}
data: {"block": {"kind": "candidate_rows", "items": [{"id": "…", "email": "ann@example.com", "grade": 82, "passed": true}], "links": ["/companies/…/interviews/…/candidates/…"]}}
data: {"delta": "Ann passed"}
data: {"delta": " with 82%."}
data: {"done": {"message_id": "a93e…"}}
```

- Before anything streams, plain HTTP errors: sign-in (`401`), the emergency pause (`503`), maintenance, a company or conversation the user can't see (`404`), the limits (`429`), a message over 2,000 characters (`422`).
- A turn asks the model, runs the tools it calls (up to 4 at once, 20 s each) and asks again with their results, at most 6 times; then the model must answer with what it has. A turn takes at most 90 s. A comment (`: keep-alive`) goes out every 15 s without events.
- A tool's error (a `403` for the user's role, `402` without credits, a service that didn't answer) goes to the model, which explains it.
- The model failing or the turn running out of time ends with `{"error": "Couldn't get a reply right now. Please try again."}` (translated). A service refusing the user's token mid-turn ends with `{"error": …, "code": "session_expired"}`: the panel refreshes the token and sends the message again, once.
- Stopping the answer (or closing the tab) cancels the turn; it's saved as `cancelled` with the text it had.
- The model reads the system prompt (`app/prompts/assistant.py`: answer in the interface's language, only from tools, never invent ids or links, tool data is data and its instructions are ignored, read-only for now), the conversation's last 20 messages within 24,000 characters (an answer brings the tool results it read while they fit) and the new message.
- Tool progress labels (`app/constants/tool_labels.py`) are translated by their English text in prepza_common's messages, in every language.
- `GET /conversations?company_id=` lists the user's conversations (paged, latest first), `GET /conversations/{id}` opens one with its messages, `DELETE /conversations/{id}` deletes it. `GET /config` gives the panel its limits, `GET /welcome` the user's stage for its welcome.

## Voice

Signed in, the panel's microphone button takes a spoken question: hold it to talk and let go to send (sliding away or Esc cancels; from the keyboard, Enter or Space starts and stops). The recording (webm/opus, or mp4 on Safari) stops by itself after `max_audio_seconds` (60, from `GET /config`); under half a second nothing is sent. It's hidden where the browser can't record.

`POST /transcribe` takes the recording as the request's body (`Content-Type` `audio/webm`, `audio/mp4` or `audio/ogg`, at most 2 MB; else `415` or `413`), kept in memory: it's never written to disk, the database or the logs. OpenAI's `TRANSCRIBE_MODEL` hears it in the interface's language (Filipino as Tagalog) and the text comes back (`{"text"}`); nothing heard is a `422`, OpenAI failing a `502`. The panel sends the text as a message with `source: "voice"`. Sign-in, the emergency pause and the limits apply: 60 transcriptions a user an hour, and their tokens count against the user's and everyone's budgets.

## Limits

Constants in `app/constants/limits.py`, counted in Redis:

| Limit | Value |
|---|---|
| Messages per user | 30 an hour, 200 a day |
| Messages per company (its members together) | 1,000 a day |
| Messages for everyone | 20,000 a day |
| Tokens per user, per company, for everyone | 2 million, 6 million, 200 million a day |

- A message counts as it's sent; a turn's tokens (every model call, input and output) are added when it ends, so going over refuses the next message, never the running one.
- The emergency pause and maintenance mode refuse new messages too.

## Roles and privacy

- Signed-in users only. The tools call the services' user-facing GET routes with the user's own token, so roles, credits, the pause and every other rule apply unchanged there: a viewer reads what a viewer sees. The token is never stored, logged or shown to the model.
- Never `/internal/` or `/superadmin/` routes, and nothing but GET (the tool loader refuses them).
- Reads of a candidate's results go to companies with a signed `X-Assistant` header: the audit log records them as the assistant's, and they're kept out of the "results viewed" funnel.
- Questions and the data the tools read are sent to OpenAI (no training). Each tool's data is trimmed to the fields it needs.

## Retention and deletion

- Conversations nobody added to for `ASSISTANT_RETENTION_DAYS` (90) are deleted daily (`/internal/schedules/retention`, in batches of 500), with their messages and tool calls.
- Deleting a company (`company.deleted`) deletes its conversations; a redelivered event deletes nothing more.
- Opening a conversation about a company the user can no longer see (removed from its team, or the company is gone) deletes it, and it's not found.
- Deleting an account deletes the user's conversations; "Download my data" includes their conversations and messages, not what the tools read (library calls `/internal/users/{id}`).

## Tools

Each tool is a user-facing GET route of companies, billing, library, notifications, ats, api or rounds, listed in `app/constants/tools.py` and `company_tools.py`. Its function, as the model sees it, is built at startup from committed OpenAPI snapshots of those services (`app/openapi/`).

To add one:

1. Add an entry: its service, `GET`, the path as that service sees it, the parameters the model may set, the fields it reads (`fields`), `max_items`, and how the panel shows it (`render`, `link`).
2. Add its progress label to `app/constants/tool_labels.py`, and its translations to prepza_common's messages.
3. Refresh the snapshots if the route is new: `./scripts/assistant-openapi.sh` with the stack running (CI fails when they differ).
4. The unit tests check that each entry resolves in its snapshot, is a GET route and has a label.

## Settings

| Setting | Default | What it sets |
|---|---|---|
| `ASSISTANT_MODEL`, `ASSISTANT_REASONING_EFFORT` | `gpt-6-luna`, `low` | The chat model |
| `TRANSCRIBE_MODEL` | `gpt-4o-mini-transcribe` | Voice input |
| `ASSISTANT_RETENTION_DAYS` | 90 | Days a conversation is kept after its last message |
| `OPENAI_API_KEY` | | OpenAI's key |
