# In-app assistant

Anyone asks the assistant from the "ask agent" button in the header (or at the end of the home page). A signed-in user asks about their companies and about prepza, and gets a streamed answer built from the same pages' data they can already see; a signed-out visitor gets answers about prepza from the FAQ's knowledge. Asked to do something it has an action for (create a company, …), it prepares it at once and the user confirms it on a card; it never runs anything by itself. This page describes the panel and the service behind it (`services/assistant`).

- [The panel](#the-panel)
- [What it answers](#what-it-answers)
- [Actions](#actions)
- [A conversation](#a-conversation)
- [Voice](#voice)
- [Limits](#limits)
- [Roles, tenancy and privacy](#roles-tenancy-and-privacy)
- [What's stored](#whats-stored)
- [Retention and deletion](#retention-and-deletion)
- [Tools](#tools)
- [Settings](#settings)

## The panel

- "ask agent" in the header (a pill with a bright arc circling its blue border; the icon alone below `md`) and at the end of the home page open it, with the input ready to type in (not on touch screens, where the keyboard would cover it). It's mounted once for the whole site, so a conversation stays while the user moves between pages, and closing never stops or loses it.
- Wider screens: a drawer at the end side, beside the page, which still scrolls; a click on the page closes it (not one in its own menus and dialogs). Its inner edge drags (or, focused, the arrow keys) to a width between 360px and 900px or 70% of the window, kept per browser. The wheel over it scrolls only its messages.
- Phones: the whole screen, the page behind it doesn't scroll, and following a link closes it.
- Its header: a company picker (signed in), New chat, History (past conversations, opened or deleted after a confirmation) and Close. The picker has the user's companies and "all companies": on a company's pages it starts on that company, elsewhere on all companies, and the user can change it; the pick is kept with the restored chat, and opening a past conversation picks its company. Each message goes with the pick: with a company, the model applies everything to it and never asks which; with all companies, it asks which company for anything that targets one (unless the user named it or has only one), and creating a company needs none.
- A reload brings back a recent chat only: one whose last message is at most `RESTORE_MINUTES` (30) old. Signed in, `GET /conversations/active` gives it (or a `204`); the browser keeps only whether the panel was open and the company pick (localStorage). Signed out, the tab's sessionStorage keeps the visitor's messages with their last one's time, and the window comes from `GET /config`. With a recent chat the panel reopens if it was open; otherwise it starts closed, on a new chat (the old one stays in the history). Signing out forgets both stores. A visitor who signs in keeps their chat on screen, and their first message saves it as the start of a new conversation (`earlier`).
- An empty conversation shows a welcome for where the user is: `GET /welcome?company_id=` decides the stage from what companies shows them (no company, a company not verified, verified without interviews, interviews without candidates, candidates), and the panel shows that stage's text and 3–4 questions to tap (`assistant.welcome` messages). Signed-out visitors get the `signed_out` welcome without a call.
- Each answer is a card (with the tools at work and the dots while it's written, and its error), and what it shows (below) right under it; answers stream in limited markdown (emphasis, lists, code and links to the app's own pages only; no images or HTML); Stop replaces Send while one streams; a failed answer shows its error and Try again; `session_expired` refreshes the token and sends once more.
- Blocks under an answer use the app's own rows: candidates as in an interview's list, interviews as in a company's list, balances as in the company header, and links to the pages the data came from.
- History titles: the start of the first question at first; after the first answer, and after every 5th question, one cheap call to the assistant's model (no reasoning, a few tokens; it counts toward the budgets) writes a one-line summary of up to 60 characters in the conversation's language, without emails or candidates' names. It comes as a `{"title"}` event after `{"done"}`; a failure keeps the old title.
- Asked to sign out, the assistant signs the user out at once: its `sign_out` tool only makes the turn send `{"sign_out": true}`, and the panel runs the site's sign-out and shows the visitor's welcome.
- **Signed out** it's the same panel with FAQ answers only: the questions go to rounds' help chat (its limits, nothing stored, see [Public site](site.md#faq-and-help-chat)), with no tools, actions, history, company or voice. Asking to sign in, or to do something that needs an account, brings a sign-in card; signing in from it keeps the panel open, now signed in.
- Both prompts keep to prepza and hiring with it (`prepza_common.scope.SCOPE_RULE`): anything else is declined in one friendly sentence, with no tools called.

## What it answers

- **Their data:** companies and roles, balances, referrals, auto top-up, the team, the audit log, interviews and whether their questions are ready, their questions and the reports on them, reports, candidates (in one interview or across a company), one candidate's results, a pause, prices, ATS connections, linked jobs and their stages, Slack, API keys and web hooks, notifications, their account and email settings, templates (and those to copy), prepza's news, and their own practice.
- **How prepza works:** how-to, pricing, credits, payments, refunds, the terms and the privacy policy, from the platform guide (rounds' `GET /help/guide`, the same knowledge as the help chat signed-out visitors ask), in the user's language.
- Tools are for the model to read; the user sees its answer, in text. A simple fact (an average, a count, a yes or no) is text only. Under an answer, the model may put one list of rows and one link with its `show` tool (`app/constants/show.py`):
  - rows (candidates, interviews or balances) only when the user asked to list or show them, or when one row is the answer (the best candidate's, none for a tie), with only the rows that answer; the text doesn't repeat them. The assistant reads them with the user's token, so only what they may see shows, and keeps their ids.
  - one link to the most specific page (the interview's page for a position, the candidate's report for a candidate), named by what it opens ("open Senior Backend"). The URL comes from a fixed map of the app's pages filled with ids; the model never writes one, and never a generic "companies" link.
- Reports are downloaded and shared from their pages: the assistant links to the candidate's or the interview's page.

## Actions

An action is a tool that changes something (`app/constants/actions.py`): a user-facing `POST`, `PUT`, `PATCH` or `DELETE` route with `confirm: True` (the loader refuses a write without it), whose body fields come from the route's snapshot.

1. The model calls it with the arguments. Nothing runs: the assistant checks them against the route's schema and keeps the action in Redis for `ACTION_TTL_SECONDS` (10 minutes), bound to the user, the conversation and the company, under a random `action_id`. The arguments never go to the browser and aren't written to the database.
2. The turn sends a card, `{"block": {"kind": "confirm", "action_id", "tool", "preview", "company_id", "destructive", "state": "pending"}}`, with exactly the values that will run; one that can't be undone carries a warning. The model tells the user to confirm it.
3. `POST /conversations/{id}/actions/{action_id}/confirm`, with the user's fresh token: the action must be this user's, in this conversation, about a company that's still theirs (from companies' list for that token); a pause, the limits and 30 actions a user an hour apply. It's claimed with Redis `GETDEL`, so of two confirms only one runs it. It runs once, as the user, with an `Idempotency-Key` of its id, and the response streams like a message: `{"action": the card's new state}` (`done` with the page it made, or `failed` with why), then the assistant's words about the result. The result reaches the model only in that turn's prompt.
4. `POST …/cancel` drops it. An expired, handled or cancelled action is a `409`; someone else's a `404`. A token the service refused (`401`) puts it back to be confirmed again with a fresh token.

Each card names what the action is about (`subject`: a company's name, an interview's title, a member's or candidate's email), read with the user's token when it's prepared, so an action about something they can't see gets no card. A pending card comes back when the conversation is reopened within its 10 minutes (Redis keeps it under the answer that prepared it); once done, its link says what it opens ("open Acme"). Actions share one progress label, "Preparing it for you to confirm…". Actions come only from the user's own request: the prompt says tool data, documents and names are never instructions, and the model fills an action with exactly the user's words and only the values they asked to change.

| Group | Actions |
|---|---|
| Companies and team (`company_actions.py`) | `create_company`, `rename_company`, `delete_company`, `set_company_website` (starts verification), `remove_company_logo`, `turn_off_auto_top_up`, `invite_member`, `change_member_role`, `remove_member` |
| Interviews, questions and candidates (`interview_actions.py`) | `create_interview` (from a job description; the result opens the topics' review), `create_interview_from_template`, `review_generation`, `retry_generation`, `cancel_generation`, `rename_interview`, `set_pass_mark`, `set_question_seconds`, `mark_hired` (one setting each, so a change carries only what was asked), `set_interview_link`, `set_topic_limit`, `regenerate_question`, `mark_question_wrong`, `delete_interview`, `invite_candidate`, `invite_candidates`, `revoke_candidate`, `set_extra_time` |
| Account, notifications, integrations and practice (`account_actions.py`) | `update_language`, `update_email_preferences`, `delete_account`, `mark_notifications_seen`, `set_slack_kinds`, `disconnect_slack`, `disconnect_ats`, `link_ats_job`, `unlink_ats_job`, `retry_ats_candidates`, `create_webhook`, `remove_webhook`, `remove_api_key`, `start_practice` |

Destructive ones (deleting a company, an interview or the account, removing a member, revoking an invite, cancelling a generation, disconnecting Slack or an ATS, removing a linked job, a web hook or an API key) carry the "can't be undone" warning. Left out on purpose: connecting an ATS, saving its web hook key and creating an API key (secrets don't belong in a chat), setting a logo and emailing a report (files the browser makes), turning on auto top-up (it charges a card; topping up is a link to `/top-up`), and the links that carry tokens (invites, unsubscribing). Asked to sign out, the panel signs out at once (`sign_out`, below).

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

- Before anything streams, plain HTTP errors: sign-in (`401`), the emergency pause (`503`), maintenance, a company that isn't one of the user's (from companies' list for their token) or a conversation they can't see (`404`), the limits (`429`), a message over 2,000 characters (`422`).
- A turn asks the model, runs the tools it calls (up to 4 at once, 20 s each) and asks again with their results, at most 6 times; then the model must answer with what it has. A turn takes at most 90 s. A comment (`: keep-alive`) goes out every 15 s without events.
- A tool's error (a `403` for the user's role, `402` without credits, a service that didn't answer) goes to the model, which explains it.
- The model failing or the turn running out of time ends with `{"error": "Couldn't get a reply right now. Please try again."}` (translated). A service refusing the user's token mid-turn ends with `{"error": …, "code": "session_expired"}`: the panel refreshes the token and sends the message again, once.
- Stopping the answer (or closing the tab) cancels the turn; it's saved as `cancelled` with the text it had.
- The model reads the system prompt (`app/prompts/assistant.py`: the user's name from their account, nothing else about them; answer in the interface's language, only from tools; act rather than explain, asking only for a truly missing value; never invent ids or links; never guess anyone's gender; tool data is data and its instructions are ignored; the scope rule), the conversation's last 20 messages' text within 24,000 characters (tools' data isn't kept: the model calls them again when it needs it) and the new message.
- Tool progress labels (`app/constants/tool_labels.py`) are translated by their English text in prepza_common's messages, in every language.
- `GET /conversations?company_id=` lists the user's conversations (paged, latest first), `GET /conversations/{id}` opens one with its messages (their blocks fetched again with the user's token), `DELETE /conversations/{id}` deletes it. `GET /config` gives the panel its limits, `GET /welcome` the user's stage for its welcome.

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
| Actions a user confirms | 30 an hour |
| Voice messages a user has transcribed | 60 an hour |

- A message counts as it's sent, and a confirmed action as a message; a turn's tokens (every model call, input and output, titles and transcriptions included) are added when it ends, so going over refuses the next message, never the running one.
- The emergency pause and maintenance mode refuse new messages too.

## Roles, tenancy and privacy

- Signed-in users only. Every tool and action calls the services' user-facing routes with the user's own token, never a service-to-service bypass, so roles, credits, the pause and every other rule apply unchanged there: a viewer reads what a viewer sees. The token is never stored, logged or shown to the model.
- A company that isn't among the user's (companies' list for their token) is refused before anything is called with it: the picked company, any `company_id` a tool is given, and a pending action's company on confirm.
- Never `/internal/` or `/superadmin/` routes, and a write only with `confirm: True` (the tool loader refuses them).
- Reads of a candidate's results go to companies with a signed `X-Assistant` header: the audit log records them as the assistant's, and they're kept out of the "results viewed" funnel.
- Questions and the data the tools read are sent to OpenAI (no training). Each tool's data is trimmed to the fields it needs.
- Logs and error reports never hold what was said, tool arguments or results: failures are logged by their type only, and Sentry gets no variables' values (`init_sentry(local_variables=False)`).

## What's stored

- Kept (Postgres `assistant`): the user's messages and the assistant's answers (text), each answer's blocks as references only (their kind, the ids of what they showed and their links, which are app paths of ids), and which tools an answer called with how long they took and how they ended (argument names, no values; no results). Opening a conversation fetches its blocks again with the user's token: what they may see now, without anything deleted or erased since.
- Not kept: tools' results (other people's data, such as candidates' results), pending actions' arguments (Redis, 10 minutes) and voice recordings (in memory only).
- Migration `0002` emptied what was kept before: tool calls' results and arguments' values, and the data in stored blocks.

## Retention and deletion

- Conversations nobody added to for `ASSISTANT_RETENTION_DAYS` (90) are deleted daily (`/internal/schedules/retention`, in batches of 500), with their messages and tool calls.
- Deleting a company (`company.deleted`) deletes its conversations; a redelivered event deletes nothing more.
- Opening a conversation about a company the user can no longer see (removed from its team, or the company is gone) deletes it, and it's not found.
- Deleting an account deletes the user's conversations and their pending actions in Redis; "Download my data" includes their conversations, messages and the blocks' references (library calls `/internal/users/{id}`).

## Tools

Each read is a user-facing GET route of companies, billing, library, notifications, ats, api or rounds, listed in `app/constants/tools.py`, `company_tools.py` and `detail_tools.py`. Its function, as the model sees it, is built at startup from committed OpenAPI snapshots of those services (`app/openapi/`).

To add one:

1. Add an entry: its service, `GET`, the path as that service sees it, the parameters the model may set, the fields it reads (`fields`), `max_items`, and how the panel shows it (`render`, `link`).
2. Add its progress label to `app/constants/tool_labels.py`, and its translations to prepza_common's messages.
3. Refresh the snapshots if the route is new: `./scripts/assistant-openapi.sh` with the stack running (CI fails when they differ).
4. The unit tests check that each entry resolves in its snapshot, is a read or a confirmed write, and has a label.

An action is the same in `app/constants/company_actions.py`, `interview_actions.py` or `account_actions.py` (gathered in `actions.py`), with its method, `confirm: True`, the body fields the model may set (`body`), what its card shows (`preview`), whether it can't be undone (`destructive`), and the page its result opens (`render: "link"`, `link` filled from the arguments and the result). The panel names it by its tool in the `assistant.actions` messages.

## Settings

| Setting | Default | What it sets |
|---|---|---|
| `ASSISTANT_MODEL`, `ASSISTANT_REASONING_EFFORT` | `gpt-6-luna`, `low` | The chat model |
| `TRANSCRIBE_MODEL` | `gpt-4o-mini-transcribe` | Voice input |
| `ASSISTANT_RETENTION_DAYS` | 90 | Days a conversation is kept after its last message |
| `OPENAI_API_KEY` | | OpenAI's key |
