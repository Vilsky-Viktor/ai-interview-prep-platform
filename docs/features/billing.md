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
- A company pays 300 credits per candidate who answers at least one question: picks an answer, not lets its time run out.
- Generating an interview is free.
- Only what works is charged: a candidate's credits are set aside on invite and given back if they never answer.
- A candidate removed before finishing (revoked, or with their interview deleted) is charged by the same rule, if they picked an answer to at least one question (rounds' `picked` count); otherwise their credits come back.
- Each invite has its own hold, so a candidate removed and invited again is charged again when they finish. Its key is the invite's own, `{interview_id}:{random}` (companies' `hold_key`), never the candidate's email, so billing keeps no candidate's email (the keys made before were rewritten that way, by billing's migration 0011 and companies' 0036 with `prepza_common.credit_keys`).
- Whenever a company gets credits (a top-up, a referral reward, a chargeback reversed), billing publishes `credits.added`: candidates its ATSs sent that weren't invited for lack of credits are invited then (see [ATS integrations](ats.md)).
- A person's first company gets 900 credits, enough for 3 candidates.
- The welcome gift is given once per inbox: case, a `+tag` and Gmail's dots don't make a new one (`app/helpers/gifts.py` in billing).

A company can have at most 3 interviews waiting without a candidate before it generates another, and generates at most 10 a day.

## Top-ups

Large top-ups buy more credits per dollar: 50% more from $250, and three times as many from $1,000.

| Top-up | Candidates | Per candidate |
|---|---|---|
| $30 | 10 | $3 |
| $150 | 50 | $3 |
| $250 | 125 | $2 |
| $1,000 | 1,000 | $1 |

- Top up on the top-up page, for any company you belong to.
- Paddle's checkout doesn't offer a discount code field.
- The home and pricing pages show the prices, their range and the free candidates as billing's catalog (`/billing/catalog`) gives them, in its currency.

Balances follow a payment as it lands:

- They are rechecked for 40 seconds after checkout.
- They catch up when the tab is back in view (an automatic top-up, a payment in another tab).
- A balance that goes up counts up to its new value, on the top-up page and on a company's interviews page.

## Automatic top-up

On the top-up page, under each balance, "Set up automatic top-up" opens the choice of a top-up and a balance to refill under; once it's on, the line shows the setting ("Automatic top-up: $30 under 300 credits") with an edit icon to change or turn it off.

- The card is saved through Paddle once.
- Running, it charges the card of whoever set it up: only they change what it buys or when. Any other owner or admin may turn it off, then turn it on with their own card (`NOT_YOUR_AUTO_TOP_UP`, a 403, otherwise).
- It is shown only when Paddle's API key and the $0 price are set (see [Setting up Paddle](#setting-up-paddle)).
- A card that declines an automatic top-up is tried again at most once a day (`AUTO_TOP_UP_RETRY_AFTER`), and the owner is told.
- A charge Paddle doesn't answer (a timeout or an error on its side) isn't counted as declined: if it went through, Paddle's webhook adds the credits; if not, it's tried again after 10 minutes (`AUTO_TOP_UP_COOLDOWN`).

## Referrals

- A company's referral link is in its referrals tab.
- Both companies get 500 credits once the new one first tops up, any amount.
- A referrer earns the reward for at most 25 referrals in any 365 days; past that, only the new company gets its 500 credits.
- If that top-up is refunded in full or charged back, both rewards are taken back.

## A company's billing tab

Owners and admins see a company's **billing** tab, before referrals; viewers don't, and its API answers them with 403.

- At the top: the available credits, the credits reserved for candidates who haven't finished, the automatic top-up setting and the top-up button.
- Two tabs under it, **history** first and **reserved (N)** beside it (`?tab=reserved`), so a long list of reserved candidates never pushes the history out of sight; only the open tab's list is loaded.
- **Reserved**: an info card on what reserved credits are, then the candidates invited who haven't finished (invited, undelivered or in progress), each opening the candidate's page. Their count comes with the company's credits (`reserved_candidates`).
- **History**: every movement of the company's credits, newest first, loading more as you scroll. Each shows the credits it moved (+3,000, −300), what it was and when:
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

1. In Paddle (start with the sandbox), create a product with a USD price for each top-up in `services/billing/app/constants/products.py` ($30, $150, $250, $1,000), and a client-side token.
2. Under Developer tools → Notifications, add a webhook destination at `https://<your domain>/api/billing/webhooks/paddle` for these events, then copy its secret key:

   | Event | Why |
   |---|---|
   | `transaction.completed` | A payment |
   | `adjustment.created`, `adjustment.updated` | Refunds and chargebacks, which take credits back |
   | `subscription.created`, `subscription.canceled` | Start and end automatic top-ups |

3. For automatic top-up, create a $0 monthly price (its checkout saves the card) and a server-side API key with permission to read and update subscriptions, and to read transactions (for invoices on the billing tab). Without both, automatic top-up isn't offered.
4. Set these in `.env`, then restart billing:

   | Setting | Value |
   |---|---|
   | `PADDLE_ENVIRONMENT` | The Paddle environment |
   | `PADDLE_CLIENT_TOKEN` | The client-side token |
   | `PADDLE_WEBHOOK_SECRET` | The webhook's secret key |
   | `PADDLE_PRICE_TOPUP_30`, `PADDLE_PRICE_TOPUP_150`, `PADDLE_PRICE_TOPUP_250`, `PADDLE_PRICE_TOPUP_1000` | The top-up prices |
   | `PADDLE_PRICE_AUTO_TOP_UP` | The $0 monthly price |
   | `PADDLE_API_KEY` | The server-side API key |

In Google Cloud, the webhook secret and the API key go into the `paddle-webhook-secret` and `paddle-api-key` secrets (see [infra/README.md](../../infra/README.md)).

- Until a price is set, its top-up button is disabled.
- Until both automatic top-up values are set, its line on the top-up page is hidden.
- Locally, Paddle reaches the webhook only through a tunnel, for example `cloudflared tunnel --url http://localhost:8090`.
