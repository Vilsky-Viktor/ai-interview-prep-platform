# Google Cloud infrastructure

Terraform for prepza on Google Cloud, in one region (`europe-west1`, Belgium) behind Google's global load balancer:

- **Cloud Run:** the frontend, nine APIs (library, generation, rounds, companies, billing, notifications, ats, api, assistant) and the generation worker; notifications' bell stream runs as its own service (`notifications-stream`, same image) so open tabs never take the capacity event pushes need. That's 12 services from 10 images. Billed per request, and idle services cost nothing.
- **Cloud SQL Postgres 18** (as locally): one database per service, with daily backups (14 kept) and point-in-time recovery (7 days back). Google Cloud refuses to delete the instance (deletion protection on the instance itself, not only in Terraform), its backups outlive it, and Google's maintenance restarts it only on Sundays at 03:00 UTC.
- **Pub/Sub:** domain events. One `events` topic is pushed to library, companies, notifications, ats, api and assistant, each getting only the event types it handles (`locals.consumes` in `pubsub.tf`; add a type there when a consumer starts handling it; a filter is capped at 256 bytes, and changing one replaces that subscription, dropping the messages it still holds, so apply when its backlog is empty; a new consumer's subscription gets only the events published after it's created), with a dead-letter topic after 50 attempts (retries back off from 10 seconds to 10 minutes, so several hours of trouble).
- **Cloud Tasks:** generation jobs on the worker, each tried up to 3 times. **Cloud Scheduler** (`jobs.tf`): outbox flushes and expired interviews every minute, generation sweeps and web hook retries every 5 minutes, key-check batches and ATS recovery every 10 minutes, daily retention (generations, candidates, the assistant's idle conversations), invite expiry and reminders and the question bank's stages, and every 10 minutes for an hour each morning the activity digest (7:00 UTC) and member reminders (8:00); a failed daily job is retried 3 times (the morning email runs aren't: the next run goes on).
- **The global load balancer:**
  - HTTPS with a Google-managed certificate;
  - `/api/<service>/` routes to each API, the MCP endpoint and its OAuth paths at the root (`/mcp`, `/authorize`, `/token`, `/register`, `/revoke` and the `/.well-known/oauth-*` metadata; exact paths, `locals.mcp_paths`) to the assistant, and everything else to the frontend;
  - Cloud CDN for static files;
  - the security headers the local nginx gateway adds (HSTS, nosniff, `X-Frame-Options`, `Referrer-Policy`, `Permissions-Policy`); the frontend sets its own Content-Security-Policy;
  - a Cloud Armor rule that blocks `/api/*/internal/`.
- **Secret Manager** for secrets, and **Artifact Registry** for images.

Outside Google Cloud: Redis on **Upstash** (rate limits, the LLM limiter, the draft cache, live notifications), **Firebase Authentication** (same project), **Resend**, **Sentry** and **Paddle**.

## Bootstrap (once)

You need `gcloud`, Docker and Terraform 1.9+ (or `docker run hashicorp/terraform`).

1. **Create the project and link billing.**
   ```bash
   gcloud projects create prepza-prod
   gcloud billing projects link prepza-prod --billing-account=<BILLING_ACCOUNT_ID>
   gcloud config set project prepza-prod
   gcloud auth application-default login
   # The budget API needs a project to bill your own login's calls to.
   gcloud auth application-default set-quota-project prepza-prod
   ```
2. **Add Firebase to the project** in the [Firebase console](https://console.firebase.google.com) ("Add project", then choose `prepza-prod`).
   - **Authentication → Sign-in method:** enable Google.
   - **Authentication → Settings → Authorized domains:** add `prepza.ai`.
   - **Authentication → Settings → User account linking:** keep "Link accounts that use the same email" (the default): the site links GitHub or LinkedIn to an existing account with the same email after the person signs in the way they did before.
   - **GitHub and LinkedIn sign-in (optional):**
     - GitHub: create an OAuth app (GitHub → Settings → Developer settings → OAuth Apps) with the callback URL `https://<authDomain>/__/auth/handler`. Set `github_client_id` and `github_client_secret` in `terraform.tfvars`.
     - LinkedIn: first upgrade the project to Identity Platform (Firebase console → Authentication → Settings; OpenID Connect providers are free for 50 monthly users, then about $0.015 each). Create a LinkedIn app with the product "Sign In with LinkedIn using OpenID Connect" and the same callback URL. Set `linkedin_client_id` and `linkedin_client_secret`.
     - Terraform (`auth.tf`) creates each provider once its client id is set.
   - **Project settings → Your apps:** add a Web app. Note its `apiKey` and `authDomain` for the frontend build; the `apiKey` is also `firebase_web_api_key` in `terraform.tfvars` (the assistant signs AI apps' users in with it).
3. **Create the bucket for Terraform's state.**
   ```bash
   gcloud storage buckets create gs://prepza-prod-terraform --location=europe-west1 --uniform-bucket-level-access
   gcloud storage buckets update gs://prepza-prod-terraform --versioning
   ```
4. **Create Redis on Upstash.** Pick the Google Cloud region `europe-west1`, and copy its `rediss://` URL.
5. **Set your variables.**
   ```bash
   cd infra/terraform
   cp terraform.tfvars.example terraform.tfvars   # fill it in
   terraform init -backend-config="bucket=prepza-prod-terraform"
   ```
   For the live site, set `paddle_environment = "production"` with the production `paddle_prices` and `paddle_client_token` (sandbox ones take no real payments), and at least one `superadmin_emails`: the emergency pause and maintenance mode are switched only from the admin zone, so Terraform refuses an empty list.

   `alert_email`, `billing_account` and `monthly_budget` set up the alerts in `monitoring*.tf`: an uptime check every minute on the site and each API's `/ready` (which checks the database only, so a Redis outage doesn't fail it), an email when one fails, an email when an event is dead-lettered, waits unhandled for over 15 minutes, or a scheduled job fails, when over 50 generation jobs stay queued for 15 minutes, when a service answers more than 5% of requests with server errors, when Paddle's or Resend's web hook is refused for its signature (a wrong secret, which the server-error alert doesn't see), when the database nears its connection limit, stays busy, runs short of memory (90%) or disk (85%), or a backup fails, when candidates' answers are slow (the interview service's p95 above 2 seconds for 10 minutes), when the analytics funnel's events wait over 15 minutes, and budget emails at 50%, 90% and 100% of the month (and when the forecast passes it). Creating the budget needs the Billing Account Costs Manager role on the billing account, which its administrator already has. `daily_generation_limit` (default 200) caps new generations a day for everyone together, a ceiling on LLM spending; 0 turns it off. `google_site_verification` and `bing_site_verification` (optional) are the tokens from Google Search Console's and Bing Webmaster Tools' meta-tag checks; the frontend adds the tags.
6. **Create the image registry first,** then push the first images. CI pushes them on every push to `main` afterwards.
   - Cloud Run runs `linux/amd64`, so build for it even on an Apple-silicon Mac.
   - Use the same tag as `image_tag` in `terraform.tfvars`.

   ```bash
   terraform apply -target=google_artifact_registry_repository.images
   gcloud auth configure-docker europe-west1-docker.pkg.dev
   REGISTRY=europe-west1-docker.pkg.dev/prepza-prod/prepza
   for service in library generation rounds companies billing notifications ats api assistant; do
     docker build --platform linux/amd64 --target prod -f services/$service/Dockerfile -t $REGISTRY/$service:first . && docker push $REGISTRY/$service:first
   done
   docker build --platform linux/amd64 --target prod -t $REGISTRY/frontend:first \
     --build-arg NEXT_PUBLIC_FIREBASE_API_KEY=<apiKey> \
     --build-arg NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=prepza-prod.firebaseapp.com \
     --build-arg NEXT_PUBLIC_FIREBASE_PROJECT_ID=prepza-prod frontend && docker push $REGISTRY/frontend:first
   ```

   Run these from the repo root.
7. **Create everything else.**
   ```bash
   terraform apply
   ```
8. **Set the secrets.** They start as `set-me`, and Terraform never overwrites them.
   ```bash
   printf '%s' "$OPENAI_API_KEY" | gcloud secrets versions add openai-api-key --data-file=-
   printf '%s' "rediss://...upstash.io:6379" | gcloud secrets versions add redis-url --data-file=-
   printf '%s' "$RESEND_API_KEY" | gcloud secrets versions add resend-api-key --data-file=-
   printf '%s' "$RESEND_WEBHOOK_SECRET" | gcloud secrets versions add resend-webhook-secret --data-file=-
   printf '%s' "$PADDLE_WEBHOOK_SECRET" | gcloud secrets versions add paddle-webhook-secret --data-file=-
   printf '%s' "$PADDLE_API_KEY" | gcloud secrets versions add paddle-api-key --data-file=-
   # The ats service's key that encrypts companies' ATS keys (a Fernet key); keep it: a new one makes them reconnect.
   python3 -c "import base64,os; print(base64.urlsafe_b64encode(os.urandom(32)).decode(), end='')" | gcloud secrets versions add ats-encryption-key --data-file=-
   # The api service's key that encrypts web hooks' signing secrets (a Fernet key); keep it: a new one makes companies add their web hooks again.
   python3 -c "import base64,os; print(base64.urlsafe_b64encode(os.urandom(32)).decode(), end='')" | gcloud secrets versions add api-encryption-key --data-file=-
   # Slack: prepza's Slack app (see docs/features/notifications.md#setting-up-slack), and the key that encrypts companies' web hooks; keep it too.
   printf '%s' "$SLACK_CLIENT_ID" | gcloud secrets versions add slack-client-id --data-file=-
   printf '%s' "$SLACK_CLIENT_SECRET" | gcloud secrets versions add slack-client-secret --data-file=-
   python3 -c "import base64,os; print(base64.urlsafe_b64encode(os.urandom(32)).decode(), end='')" | gcloud secrets versions add slack-encryption-key --data-file=-
   ```

   Terraform makes the generated ones itself: each service's secret for internal calls, the database passwords, `analytics-salt`, `preview-secret` (signs the frontend's link-preview titles) and `email-link-secret` (signs the unsubscribe links in emails; replacing it breaks the links in emails already sent).

   Services read `latest` when they start, so redeploy (step 9) after setting secrets.
9. **Run the migrations, then restart the services** so they pick up the secrets.
   ```bash
   for db in library generation rounds companies billing notifications ats api assistant; do
     gcloud run jobs execute $db-migrate --region=europe-west1 --wait
   done
   # A new revision of each service reads the secrets you just set.
   for service in frontend library generation rounds companies billing notifications notifications-stream ats api assistant generation-worker; do
     gcloud run services update $service --region=europe-west1 --update-labels=restarted=$(date +%s)
   done
   ```
10. **Point the domain at the load balancer.** In GoDaddy's DNS, add an **A record** for `@` with the value of `terraform output site_ip`. Google then issues the certificate, which can take up to about an hour:
    ```bash
    gcloud compute ssl-certificates describe prepza --global --format='value(managed.status)'
    ```
    Until the certificate is active, the uptime checks fail and their alerts email you; they clear by themselves once the site answers.
11. **Update the services that call back to the site:**
    - **Paddle:** the webhook destination is `https://prepza.ai/api/billing/webhooks/paddle`, for `transaction.completed`, `adjustment.created`, `adjustment.updated`, `subscription.created` and `subscription.canceled`. The adjustments are refunds and chargebacks, which take the credits back; the subscriptions start and end automatic top-ups. Once deployed, send Paddle's test notification to it: it must be accepted (a refused signature means `paddle-webhook-secret` is wrong, and the alert below fires).
    - **Resend:** the `prepza.ai` sending domain is already verified; verify `mail.prepza.ai` too, the optional emails' sender (see [Email deliverability](#email-deliverability)). Add a webhook at `https://prepza.ai/api/notifications/webhooks/resend` for `email.bounced`, `email.complained` and `email.suppressed`; its signing secret is `resend-webhook-secret` in step 8. Once deployed, send a test event from Resend and check it's accepted.
    - **Sentry:** set `backend_sentry_dsn` in `terraform.tfvars`.

12. **Connect GitHub for deploys.** In the repository's **Settings → Secrets and variables → Actions → Variables**, add:
    - **From Terraform:** everything in `terraform output github_variables`, which gives `GCP_PROJECT_ID`, `GCP_REGION`, `GCP_WORKLOAD_IDENTITY_PROVIDER`, `GCP_DEPLOY_SERVICE_ACCOUNT` and `SITE_URL`.
    - **From Firebase:** `NEXT_PUBLIC_FIREBASE_API_KEY` and `NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN`, from the web app in step 2.
    - **Optionally:** `FRONTEND_SENTRY_DSN` for the frontend.

    These are variables, not secrets: none of them grants access. GitHub's signed token is what lets the pipeline in, and only for `main` and the `v*` tags of this repository.
13. **Protect the version tags.** A tag deploys, so only you should be able to make one. In **Settings → Rules → Rulesets**, add a **tag ruleset**:
    - **Target tags:** include by pattern `v*`.
    - **Rules:** restrict creations, restrict updates and restrict deletions.
    - **Bypass list:** Repository admin, so you can still create them.
14. **Optionally, require an approval for deploys.** Deploys run in the `production` environment, which GitHub creates on the first deploy. In **Settings → Environments → production**, add yourself under **Required reviewers**; each deploy then waits for your click. Rulesets and required reviewers on a private repository need a paid GitHub plan.

## Email deliverability

Emails go out through Resend in two streams, each from its own domain, so spam complaints about the optional ones can't hurt the reputation of the service ones:

| Stream | Emails | Sender (`terraform.tfvars`) |
| --- | --- | --- |
| Service | candidate invites and reminders, shared reports, failed automatic top-ups, contact messages | `mail_from = "prepza. <no-reply@prepza.ai>"` |
| Optional | the activity digest and reminders (later product updates and offers) | `mail_from_updates = "prepza. <updates@mail.prepza.ai>"` |

The DNS records below are what Gmail, Yahoo (their 2024 rules for bulk senders) and Outlook check. Add them in GoDaddy's DNS, where a record's name is relative to `prepza.ai` (`send` means `send.prepza.ai`):

1. **Add both domains in Resend, in the EU region.** At resend.com/domains, add `prepza.ai` and `mail.prepza.ai` with the region **Ireland (eu-west-1)**: a domain's region is set when it's added (to change it, delete the domain and add it again). Each domain's page lists its exact records: copy the values from there, as the DKIM key is unique to each domain.
2. **Sending (SPF and the bounce address).** Two CNAME records per domain point the `send` and `rsend` subdomains at Resend, which publishes the SPF record and receives the bounces there, not on `prepza.ai` itself:

   | Type | Name | Value |
   | --- | --- | --- |
   | CNAME | `send` | `send.forge.rmta.net` |
   | CNAME | `rsend` | `rsend-euw1.forge.rmta.net` (the EU region's host) |
   | CNAME | `send.mail` | `send.forge.rmta.net` |
   | CNAME | `rsend.mail` | `rsend-euw1.forge.rmta.net` |

   A name has at most one SPF record. Whatever receives mail for `@prepza.ai` (the mailbox behind `hello@prepza.ai`) adds its own MX and SPF records on `@`, as its provider says.
3. **DKIM.** One TXT record per domain, with the key from Resend's page:

   | Type | Name | Value |
   | --- | --- | --- |
   | TXT | `resend._domainkey` | `p=MIGfMA0GCSqGSIb3DQEB…` (prepza.ai's key) |
   | TXT | `resend._domainkey.mail` | `p=MIGfMA0GCSqGSIb3DQEB…` (mail.prepza.ai's key) |

   Click **Verify** on each domain's page once the records are in; both should show "Verified".
4. **DMARC.** One record on `prepza.ai` covers `mail.prepza.ai` too. Start by only collecting reports, sent to an address you read:

   | Type | Name | Value |
   | --- | --- | --- |
   | TXT | `_dmarc` | `v=DMARC1; p=none; rua=mailto:dmarc@prepza.ai; adkim=r; aspf=r` |

   After 2–4 weeks of reports showing every legitimate sender passing (Resend, and the mailbox provider of `hello@prepza.ai`), move to `p=quarantine`, and later to `p=reject`.
5. **Turn tracking off.** On each domain's page in Resend, under **Configuration**, keep **Click tracking** and **Open tracking** off: click tracking rewrites links into redirects through another domain, and the open pixel is an image from elsewhere; both look like spam. Emails link only to `prepza.ai`.
6. **Check it.** Send an invite and a digest to the address mail-tester.com gives you and aim for 10/10; in Gmail, **Show original** should say `PASS` for SPF, DKIM and DMARC. Add `prepza.ai` to [Google Postmaster Tools](https://postmaster.google.com) (verified with one more TXT record) and keep the spam rate under 0.1%, never reaching 0.3%; Outlook's [SNDS](https://sendersupport.olc.protection.outlook.com/snds/) shows the same for Microsoft.

What the emails do themselves: each has a plain-text part next to the HTML, `Auto-Submitted: auto-generated`, and a Reply-To that someone reads (the member who shared a report, the visitor for contact messages, otherwise `CONTACT_EMAIL`). Only emails the recipient may stop (the digest, reminders, a candidate's reminder) carry the one-click `List-Unsubscribe` headers; a spam complaint about the digest or reminders turns them off for that user (see [Notifications and emails](../docs/features/notifications.md#unsubscribing)).

## Deploys

- **Pull requests:** CI runs on every push, and a new push cancels the previous run. It tests and builds only what changed: ruff always; a changed service's unit tests and image; a changed frontend's lint, types, translations check, unit tests and image; and the smoke, integration and page tests on the whole stack when any part, the stack or its tests changed (see [Testing](../docs/testing.md#ci)).
- **Merging to `main`:** the same CI runs again on the merged code, compared with the last commit it passed on, and pushes the 10 production images for `linux/amd64`, tagged with the commit: the changed ones are built, the others are that commit's images with the new tag added. Nothing is deployed.
- **Releasing:** tag a commit on `main` that CI passed on, the last commit of a push, and push the tag:
  ```bash
  git tag v1.4.0 && git push origin v1.4.0
  ```
  [`.github/workflows/deploy.yml`](../.github/workflows/deploy.yml) then checks that the tag is on `main` and CI passed on it, gives that commit's images the version as a tag (nothing is rebuilt), runs the `db-roles` job and then the 9 migration jobs, moves all 12 services to the images, smoke-tests the site and creates a GitHub release with the changes since the last tag.

A failed step stops the deploy, and the services keep running the previous images.

- **Rolling back:** in **Actions → Deploy → Run workflow**, enter an earlier version, for example `v1.3.2`, and leave **Run migrations** off. It redeploys that version's images in about a minute, on the newer schema (an older version's migrations would fail on it). So this is safe only while the newer migrations didn't remove anything the older code needs: keep migrations additive. Tick **Run migrations** only to redeploy a version whose migrations haven't run. For one service, you can also move it to an earlier revision in the Cloud Run console.
- **Terraform never touches image tags,** so applying an infrastructure change doesn't roll anything back.
- **Pinned dependencies:** workflow actions are pinned by commit and the Dockerfiles' base images by digest; [`.github/dependabot.yml`](../.github/dependabot.yml) opens weekly pull requests that update them (base images by minor and patch versions only). Merge one once CI passes.

## Restore drill

A backup is only proven by restoring it. Run `scripts/ops/restore-drill.sh prepza-prod` before launch, and then every quarter. It needs `gcloud`, `cloud-sql-proxy` and `psql`, and it:
1. Restores the latest backup into a temporary instance.
2. Reads each service's main tables through the Cloud SQL Auth Proxy.
3. Deletes the temporary instance, even if a step fails.

It costs a few cents: the temporary instance runs for about 15 minutes.

For an actual recovery, Cloud SQL can also restore to any second of the last 7 days (point-in-time recovery), for example to just before a bad deploy:

```bash
gcloud sql instances clone prepza prepza-recovered --point-in-time="2026-10-02T12:00:00Z"
```

Then point `DATABASE_URL` at the clone, or copy the needed data back.

## Notes

- **Service addresses:** services reach each other at their Cloud Run addresses, which are known in advance (`https://<service>-<project number>.europe-west1.run.app`).
- **Who can call what:**
  - Public services take outside traffic only through the load balancer (ingress "internal and Cloud Load Balancing"), so Cloud Armor's rules always apply; their `run.app` addresses refuse the internet. The generation worker takes only Google's calls.
  - Calls between services go out through the private network in `network.tf` (Direct VPC egress, all traffic), so they arrive as internal; the internet (OpenAI, Resend, Paddle, Upstash) is reached through its Cloud NAT, about $1–5 a month at this size. The NAT gives each instance ports as it needs them (64 to 4096), so an instance isn't capped at about 64 connections to one address.
  - Calls between services also carry signed service tokens.
  - Pub/Sub, Cloud Tasks and Scheduler sign as the `prepza-invoker` account, which the services check.
- **Database users:** each service connects as its own Postgres user (named after its database) that owns only that database; other users can't even connect to it. The `prepza` user is the instance's admin and is used only by the `db-roles` job (`db_roles.tf`, `services/library/app/jobs/db_roles.py`), which creates those users and moves ownership to them. The deploy pipeline runs it before migrations; it's safe to repeat. **When first applying this over an existing database,** run it right after `terraform apply`, before any service restarts: `gcloud run jobs execute db-roles --region=europe-west1 --wait`. Until it has run, new instances can't connect, since their URLs already name the new users. Locally, Docker Compose keeps the one `prepza` user.
- **Least privilege:** each service runs as its own account (`prepza-<service>`, see `iam.tf`) that can read only its own secrets and its own database's URL. The frontend has no permissions; only the backend services publish events, and only the generation services queue tasks. The assistant also reads Firebase accounts (`roles/firebaseauth.viewer`) and signs as itself (`roles/iam.serviceAccountTokenCreator` on its own account, through the `iamcredentials` API), to sign the users of AI apps connected over MCP in with a custom token ([AI apps over MCP](../docs/features/mcp.md#calling-the-services-as-the-user)). Migrations run as their service's account. Applying this over the old shared `prepza-runtime` account moves every service to its own account, then deletes the old one.
- **App settings:** Terraform passes `DAILY_GENERATION_LIMIT` (from `daily_generation_limit`), and the assistant's `SITE_URL` and `FIREBASE_WEB_API_KEY` (from `domain` and `firebase_web_api_key`), but none of the other settings in `.env.example`: the AI models and reasoning efforts (`INTERVIEW_MODEL`, `VERIFY_MODEL`, `HELP_MODEL` and their `*_REASONING_EFFORT`), `INTERVIEW_QUESTIONS_PER_TOPIC`, `TEMPLATE_QUESTIONS_PER_TOPIC`, `MAX_TOPICS`, `MAX_SUBTOPICS`, `LLM_REQUESTS_PER_SECOND` and the per-user limits. The services run on their code defaults, which match `.env.example`. To change one in production, add it to the service's entry in `env.tf`.
- **Dead-lettered events:** an event a consumer failed on 50 times waits 7 days in the `events-dead-letter` subscription, and an alert emails you while any wait there. After fixing the consumer, replay them to the `events` topic with their attributes (the type), which acknowledges each one republished:

  ```bash
  # One at a time, so each is acknowledged well within the subscription's 10-second deadline.
  while m=$(gcloud pubsub subscriptions pull events-dead-letter --limit=1 --format=json | jq -c '.[0] // empty') && [ -n "$m" ]; do
    attrs=$(jq -r '.message.attributes | with_entries(select(.key | startswith("CloudPubSubDeadLetter") | not)) | to_entries | map("\(.key)=\(.value)") | join(",")' <<<"$m")
    gcloud pubsub topics publish events --message="$(jq -r .message.data <<<"$m" | base64 -d)" --attribute="$attrs" &&
      gcloud pubsub subscriptions ack events-dead-letter --ack-ids="$(jq -r .ackId <<<"$m")"
  done
  ```

  The replay goes to every consumer subscribed to that type, not only the one that failed. `candidate.finished` and `company.deleted` reach notifications, ats and api, `candidate.rescored` reaches all three too (notifications ignores it), and `candidate.removed` reaches notifications and ats, so a replay of those also reaches the consumers that already handled them; each consumer handles a redelivered event safely, so that changes nothing twice (see [Architecture](../docs/architecture.md#events)).
- **Generation jobs:** a job may run up to 25 minutes, under Cloud Tasks' 30-minute limit. The queue tries a task up to 3 times (`jobs.tf`), for a delivery that fails before the job starts, such as a worker restarting; a job first moves its generation from queued to running in one atomic step, so a repeated delivery does nothing. A generation that fails once running is retried by the user.
- **Database connections:** Cloud SQL starts at `db-g1-small` with 200 connections allowed, 20 kept free. Each API process holds up to 10 connections (generation and the worker 14, notifications, ats and api 4); the services' `max` instances fit within the rest, and the plan fails if they don't (`database.tf`): today at most 132 of the 180. A deploy moves the services one at a time and runs each one's old instances until their requests end, so the plan also fails if a deploy at the instance limits could pass the 200: the peak, plus the old worker and bell-stream instances (their requests outlast the deploy), plus the largest other service; today 188. The APIs with a pool of 10 take 40 requests at once per instance, so a busy one scales out rather than queueing on its pool; the worker takes 10 jobs on each of its 2 instances, the queue's 20 at once. Raise `db_tier` (and `db_max_connections`), or add PgBouncer, before allowing more instances or once services often run near their `max`.
- **High availability:** `db_high_availability = true` adds a standby in another zone, at about double the database cost.
- **Not yet tried on a real project:** `terraform validate` passes, but some settings may need a small adjustment on the first `apply`. The ones most likely to need it are the load balancer's backend protocol for Cloud Run, and Cloud Armor on the CDN backend.
