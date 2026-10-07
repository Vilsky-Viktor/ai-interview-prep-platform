# Credits and payments

Companies pay per candidate from a wallet of credits. There are no subscriptions.

- [Credits](#credits)
- [Top-ups](#top-ups)
- [Automatic top-up](#automatic-top-up)
- [Referrals](#referrals)
- [Refunds and chargebacks](#refunds-and-chargebacks)
- [Setting up Paddle](#setting-up-paddle)

## Credits

- $1 buys 100 credits. Credits never expire.
- A company pays 300 credits per candidate who answers at least one question.
- Generating an interview is free.
- Only what works is charged: a candidate's credits are set aside on invite and given back if they never answer.
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

Balances follow a payment as it lands:

- They are rechecked for 40 seconds after checkout.
- They catch up when the tab is back in view (an automatic top-up, a payment in another tab).
- A balance that goes up counts up to its new value, on the top-up page and on a company's interviews page.

## Automatic top-up

On the top-up page, under each balance ("Automatic top-up: off"), choose a top-up and a balance to refill under.

- The card is saved through Paddle once.
- It is shown only when Paddle's API key and the $0 price are set (see [Setting up Paddle](#setting-up-paddle)).
- A card that declines an automatic top-up is tried again at most once a day (`AUTO_TOP_UP_RETRY_AFTER`), and the owner is told.

## Referrals

- A company's referral link is in its referrals tab.
- Both companies get 500 credits once the new one first tops up, any amount.
- If that top-up is refunded in full or charged back, both rewards are taken back.

## Refunds and chargebacks

Refunds and chargebacks in Paddle take back the credits they bought.

## Setting up Paddle

`billing` sells through [Paddle](https://www.paddle.com), which is the merchant of record: it handles VAT and sales tax.

1. In Paddle (start with the sandbox), create a product with a USD price for each top-up in `services/billing/app/constants/products.py` ($30, $150, $250, $1,000), and a client-side token.
2. Under Developer tools → Notifications, add a webhook destination at `https://<your domain>/api/billing/webhooks/paddle` for these events, then copy its secret key:

   | Event | Why |
   |---|---|
   | `transaction.completed` | A payment |
   | `adjustment.created`, `adjustment.updated` | Refunds and chargebacks, which take credits back |
   | `subscription.created`, `subscription.canceled` | Start and end automatic top-ups |

3. For automatic top-up, create a $0 monthly price (its checkout saves the card) and a server-side API key with permission to read and update subscriptions. Without both, automatic top-up isn't offered.
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
