# Credits and payments

Companies pay per candidate from a wallet of credits. There's no paid subscription: the optional automatic top-up saves the card through Paddle as a $0 subscription, and charges only the top-ups.

- [Credits](#credits)
- [Top-ups](#top-ups)
- [Automatic top-up](#automatic-top-up)
- [Referrals](#referrals)
- [A company's billing tab](#a-companys-billing-tab)
- [Refunds and chargebacks](#refunds-and-chargebacks)
- [Deleting a company](#deleting-a-company)
- [Setting up Paddle](#setting-up-paddle)

## Credits

- $1 buys 100 credits. Credits never expire.
- A company pays 500 credits ($5) per candidate who answers at least one question: picks an answer, not lets its time run out.
- Generating an interview is free.
- Only what works is charged: a candidate's credits are set aside on invite and given back if they never answer.
- A candidate removed before finishing (revoked, or with their interview deleted) is charged by the same rule, if they picked an answer to at least one question (rounds' `picked` count); otherwise their credits come back.
- Credits set aside for an invite that then fails (the email limits, saving it, starting it, or billing's answer lost on the way) come back at once: a new invite's, or an expired one's sent again or started again (expiry won't release an expired invite a second time). An invite's earlier hold stays.
- An automatic top-up that a hold calls for is charged after billing answers the hold, so an invite never waits on Paddle.
- Each invite has its own hold, so a candidate removed and invited again is charged again when they finish. Its key is the invite's own, `{interview_id}:{random}` (companies' `hold_key`), never the candidate's email, so billing keeps no candidate's email (the keys made before were rewritten that way, by billing's migration 0011 and companies' 0036 with `prepza_common.credit_keys`).
- Whenever a company gets credits (a top-up, a referral reward, a chargeback reversed), billing publishes `credits.added`: candidates its ATSs sent that weren't invited for lack of credits are invited then (see [ATS integrations](ats.md)).
- A person's first company gets 1,500 credits, enough for 3 candidates; on the site, creating it asks them to show they're a person first ([the "I'm not a robot" check](../architecture.md#the-im-not-a-robot-check)). The credits come once per owner's email, so creating any company needs a verified email: a sign-in that doesn't verify it (GitHub) is told to confirm it first, with the link sent when they signed in, and one confirmed meanwhile counts without signing in again.
- The welcome gift is given once per inbox: case, a `+tag` and Gmail's dots don't make a new one (`app/helpers/gifts.py` in billing). A new company asks for it up to 3 times, with the same company: billing gives it once per company, so an answer lost on the way neither loses the gift nor the referral. Only when every try fails is the company removed again, so its name stays free.

Until its first top-up, a company can have 1 generated interview waiting without a candidate before it generates another, and generates at most 3 a day; after it, 5 waiting and 10 a day. Interviews copied from templates don't count, and retrying a failed generation isn't a new one.

## Top-ups

Large top-ups buy more credits per dollar: each top-up has its own price per candidate (`CANDIDATE_PRICE_TIERS`), and buys whole candidates at it.

| Top-up | Candidates | Per candidate |
|---|---|---|
| $50 | 10 | $5 |
| $200 | 50 | $4 |
| $600 | 200 | $3 |
| $1,000 | 500 | $2 |

Saved automatic top-ups were moved to these by billing's migration 0012 ($30 to $50, $150 to $200, $250 to $600), each threshold keeping its number of candidates.

- Top up on the top-up page, for any company you belong to.
- Billing makes each top-up's checkout (a Paddle transaction naming the company and the buyer), after companies checks the buyer is its owner or an admin (`POST /companies/{id}/billing/checkout`); the browser only opens it, so it can't send the money to another wallet or record someone else as the buyer. A paid transaction billing didn't make (its origin isn't `api`), or one into a company deleted meanwhile, adds no credits and is logged as an error, to refund.
- Paddle's checkout doesn't offer a discount code field.
- The home and pricing pages show the prices, their range and the free candidates as billing's catalog (`/billing/catalog`) gives them, in its currency.

Balances follow a payment as it lands:

- They are rechecked for 40 seconds after checkout.
- They catch up when the tab is back in view (an automatic top-up, a payment in another tab).
- A balance that goes up counts up to its new value, on the top-up page and on a company's interviews page.

## Automatic top-up

On the top-up page, under each balance, "Set up automatic top-up" opens the choice of a top-up and a balance to refill under; once it's on, the line shows the setting ("Automatic top-up: $50 under 500 credits") with an edit icon to change or turn it off.

- The card is saved through Paddle once.
- Running, it charges the card of whoever set it up: only they change what it buys or when. Any other owner or admin may turn it off, then turn it on with their own card (`NOT_YOUR_AUTO_TOP_UP`, a 403, otherwise).
- Turning it off (by a member, by removing or demoting the member whose card pays, or by deleting the company or that member's account) cancels its Paddle subscription first and only then forgets it; a subscription Paddle already ended counts as cancelled. If Paddle can't cancel it, it stays on and the action fails, to be tried again, so the card is never left saved with nothing pointing at it.
- It is shown only when Paddle's API key and the $0 price are set (see [Setting up Paddle](#setting-up-paddle)).
- A card that declines an automatic top-up is tried again at most once a day (`AUTO_TOP_UP_RETRY_AFTER`), and the owner is told.
- A charge Paddle doesn't answer (a timeout or an error on its side) isn't counted as declined: if it went through, Paddle's webhook adds the credits; either way no other charge follows until a charge's credits have come, for at most a day (`AUTO_TOP_UP_UNCREDITED_WAIT`), so a late or failing webhook never charges the card again and again. Once they've come, the next charge waits at least 10 minutes (`AUTO_TOP_UP_COOLDOWN`).

## Referrals

- A company's referral link is in its referrals tab.
- Both companies get 1,000 credits (2 candidates) once the new one first tops up, any amount.
- The link asks the visitor first (a toast with **Keep** and **No thanks**), as the cookie serves the referral and not the page they asked for; kept, its code goes in a cookie (`prepza_ref`, 30 days), which companies reads when the visitor creates a company, on the site or through the in-app assistant: confirming the assistant's action passes the cookie on (only a code that reads right). AI apps connected over MCP have no browser cookie, so a company they create records no referral.
- A referrer earns the reward for at most 25 referrals in any 365 days; past that, only the new company gets its 1,000 credits.
- If that top-up is refunded in full or charged back, both rewards are taken back.

A balance shows short from a thousand credits up ("3.5K", in the language's own way), and says the whole amount on hover ("Current balance: 3,549"), wherever it appears: the company's header, the billing and top-up pages and the assistant's answers.

## A company's billing tab

Owners and admins see a company's **billing** tab, before referrals; viewers don't, and its API answers them with 403.

- At the top: the available credits, the credits reserved for candidates who haven't finished, the automatic top-up setting and the top-up button.
- Two tabs under it, **history** first and **reserved (N)** beside it (`?tab=reserved`), so a long list of reserved candidates never pushes the history out of sight; only the open tab's list is loaded.
- **Reserved**: an info card on what reserved credits are, then the candidates invited who haven't finished (invited, undelivered or in progress), each opening the candidate's page. Their count comes with the company's credits (`reserved_candidates`).
- **History**: every movement of the company's credits, newest first, loading more as you scroll. Each shows the credits it moved (+5,000, −500), what it was and when:
  - a top-up: what was paid (tax included), whether it was automatic, and its invoice, opened through a temporary Paddle link made on request;
  - a candidate: the candidate and their test, opening the candidate's page, or "A deleted candidate" when the invite is gone;
  - a refund, a chargeback, a chargeback reversed: the money it moved;
  - a referral reward, a referral reward taken back, the welcome gift.

Billing's history entries keep the money a top-up, refund or chargeback moved (`total`, in minor units, and `currency`) and whether a top-up was automatic; entries from before that was kept have the money of their top-up only. Companies' `GET /companies/{id}/billing/history`, `/billing/reserved` and `/billing/invoice?transaction_id=` serve the tab: the history comes from billing's internal `GET /internal/companies/{id}/history`, its candidates are matched to their invites by the key of their credits in one query, and the invoice from `GET /internal/companies/{id}/invoice`, which checks the transaction topped up that company.

## Refunds and chargebacks

Refunds and chargebacks in Paddle take back the credits they bought.

## Deleting a company

Deleting a company deletes its credits: billing's internal `DELETE /internal/companies/{id}` removes the wallet, its holds and its history, and turns off automatic top-up. Purchases stay on record, and nothing is refunded. Before it's deleted, the owner sees how many credits are lost: the remove dialog, and the assistant's delete card, read the company's balance (`GET /companies/{id}/credits`, whose `candidates` is how many candidates the available credits pay for, worked out by billing) and add "Its 900 credits (about 3 candidates) will be lost and aren't refunded." when there are any.

## Setting up Paddle

`billing` sells through [Paddle](https://www.paddle.com), which is the merchant of record: it handles VAT and sales tax.

1. In Paddle (start with the sandbox), create a product with a USD price for each top-up in `services/billing/app/constants/products.py` ($50, $200, $600, $1,000), and a client-side token.
2. Under Developer tools → Notifications, add a webhook destination at `https://<your domain>/api/billing/webhooks/paddle` for these events, then copy its secret key:

   | Event | Why |
   |---|---|
   | `transaction.completed` | A payment |
   | `adjustment.created`, `adjustment.updated` | Refunds and chargebacks, which take credits back |
   | `subscription.created`, `subscription.canceled` | Start and end automatic top-ups |

3. Create a server-side API key with permission to read and write transactions (billing makes every top-up's checkout, and reads invoices for the billing tab) and to read and update subscriptions (automatic top-up). For automatic top-up, also create a $0 monthly price (its checkout saves the card); without it and the key, automatic top-up isn't offered.
4. Set these in `.env`, then restart billing:

   | Setting | Value |
   |---|---|
   | `PADDLE_ENVIRONMENT` | The Paddle environment |
   | `PADDLE_CLIENT_TOKEN` | The client-side token |
   | `PADDLE_WEBHOOK_SECRET` | The webhook's secret key |
   | `PADDLE_PRICE_TOPUP_50`, `PADDLE_PRICE_TOPUP_200`, `PADDLE_PRICE_TOPUP_600`, `PADDLE_PRICE_TOPUP_1000` | The top-up prices |
   | `PADDLE_PRICE_AUTO_TOP_UP` | The $0 monthly price |
   | `PADDLE_API_KEY` | The server-side API key |

In Google Cloud, the webhook secret and the API key go into the `paddle-webhook-secret` and `paddle-api-key` secrets (see [infra/README.md](../../infra/README.md)).

- Until a price is set, its top-up button is disabled.
- Until both automatic top-up values are set, its line on the top-up page is hidden.
- Locally, Paddle reaches the webhook only through a tunnel, for example `cloudflared tunnel --url http://localhost:8090`.
