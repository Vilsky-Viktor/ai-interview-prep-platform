# Google Cloud infrastructure

Terraform for prepza on Google Cloud, in one region (`europe-west1`, Belgium) behind Google's global load balancer:

- **Cloud Run:** the frontend, six APIs, the generation worker and notifications, whose bell stream runs as its own service (`notifications-stream`, same image) so open tabs never take the capacity event pushes need. Billed per request, and idle services cost nothing.
- **Cloud SQL Postgres 18** (as locally): one database per service, with daily backups and point-in-time recovery.
- **Pub/Sub:** domain events. One `events` topic is pushed to library, companies, notifications, ats and api, each getting only the event types it handles (`pubsub.tf`; add a type there when a consumer starts handling it), with a dead-letter topic after 50 attempts (retries back off from 10 seconds to 10 minutes, so several hours of trouble).
- **Cloud Tasks:** generation jobs on the worker, each tried up to 3 times. **Cloud Scheduler:** sweeps, retention, the question bank's stages, and candidate invite reminders and expiry; a failed daily job is retried 3 times.
- **The global load balancer:**
  - HTTPS with a Google-managed certificate;
  - `/api/<service>/` routes to each API, and everything else to the frontend;
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
   - **Project settings → Your apps:** add a Web app. Note its `apiKey` and `authDomain` for the frontend build.
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
   `alert_email`, `billing_account` and `monthly_budget` set up the alerts in `monitoring.tf`: an uptime check every minute on the site and each API's `/ready` (which checks the database only, so a Redis outage doesn't fail it), an email when one fails, an email when an event is dead-lettered or a scheduled job fails, when a service answers more than 5% of requests with server errors, or when the database nears its connection limit or stays busy, and budget emails at 50%, 90% and 100% of the month (and when the forecast passes it). Creating the budget needs the Billing Account Costs Manager role on the billing account, which its administrator already has. `daily_generation_limit` (default 200) caps new generations a day for everyone together, a ceiling on LLM spending; 0 turns it off. `google_site_verification` and `bing_site_verification` (optional) are the tokens from Google Search Console's and Bing Webmaster Tools' meta-tag checks; the frontend adds the tags.
6. **Create the image registry first,** then push the first images. CI pushes them on every push to `main` afterwards.
   - Cloud Run runs `linux/amd64`, so build for it even on an Apple-silicon Mac.
   - Use the same tag as `image_tag` in `terraform.tfvars`.

   ```bash
   terraform apply -target=google_artifact_registry_repository.images
   gcloud auth configure-docker europe-west1-docker.pkg.dev
   REGISTRY=europe-west1-docker.pkg.dev/prepza-prod/prepza
   for service in library generation rounds companies billing notifications ats api; do
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

   Services read `latest` when they start, so redeploy (step 9) after setting secrets.
9. **Run the migrations, then restart the services** so they pick up the secrets.
   ```bash
   for db in library generation rounds companies billing notifications ats api; do
     gcloud run jobs execute $db-migrate --region=europe-west1 --wait
   done
   # A new revision of each service reads the secrets you just set.
   for service in frontend library generation rounds companies billing notifications notifications-stream ats api generation-worker; do
     gcloud run services update $service --region=europe-west1 --update-labels=restarted=$(date +%s)
   done
   ```
10. **Point the domain at the load balancer.** In GoDaddy's DNS, add an **A record** for `@` with the value of `terraform output site_ip`. Google then issues the certificate, which can take up to about an hour:
    ```bash
    gcloud compute ssl-certificates describe prepza --global --format='value(managed.status)'
    ```
    Until the certificate is active, the uptime checks fail and their alerts email you; they clear by themselves once the site answers.
11. **Update the services that call back to the site:**
    - **Paddle:** the webhook destination is `https://prepza.ai/api/billing/webhooks/paddle`, for `transaction.completed`, `adjustment.created`, `adjustment.updated`, `subscription.created` and `subscription.canceled`. The adjustments are refunds and chargebacks, which take the credits back; the subscriptions start and end automatic top-ups.
    - **Resend:** the `prepza.ai` sending domain is already verified. Add a webhook at `https://prepza.ai/api/notifications/webhooks/resend` for `email.bounced`, `email.complained` and `email.suppressed`; its signing secret is `resend-webhook-secret` in step 8.
    - **Sentry:** set `sentry_dsn` in `terraform.tfvars`.

12. **Connect GitHub for deploys.** In the repository's **Settings → Secrets and variables → Actions → Variables**, add:
    - **From Terraform:** everything in `terraform output github_variables`, which gives `GCP_PROJECT_ID`, `GCP_REGION`, `GCP_WORKLOAD_IDENTITY_PROVIDER`, `GCP_DEPLOY_SERVICE_ACCOUNT` and `SITE_URL`.
    - **From Firebase:** `NEXT_PUBLIC_FIREBASE_API_KEY` and `NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN`, from the web app in step 2.
    - **Optionally:** `NEXT_PUBLIC_SENTRY_DSN` for the frontend.

    These are variables, not secrets: none of them grants access. GitHub's signed token is what lets the pipeline in, and only for `main` and the `v*` tags of this repository.
13. **Protect the version tags.** A tag deploys, so only you should be able to make one. In **Settings → Rules → Rulesets**, add a **tag ruleset**:
    - **Target tags:** include by pattern `v*`.
    - **Rules:** restrict creations, restrict updates and restrict deletions.
    - **Bypass list:** Repository admin, so you can still create them.
14. **Optionally, require an approval for deploys.** Deploys run in the `production` environment, which GitHub creates on the first deploy. In **Settings → Environments → production**, add yourself under **Required reviewers**; each deploy then waits for your click. Rulesets and required reviewers on a private repository need a paid GitHub plan.

## Deploys

- **Pull requests:** CI (lint, tests, image builds, and the smoke, integration and page tests on the whole stack) runs on every push, and a new push cancels the previous run.
- **Merging to `main`:** the same CI runs again on the merged code, and pushes the 7 production images for `linux/amd64`, tagged with the commit. Nothing is deployed.
- **Releasing:** tag a commit on `main` that CI passed on, the last commit of a push, and push the tag:
  ```bash
  git tag v1.4.0 && git push origin v1.4.0
  ```
  [`.github/workflows/deploy.yml`](../.github/workflows/deploy.yml) then checks that the tag is on `main` and CI passed on it, gives that commit's images the version as a tag (nothing is rebuilt), runs the 6 migration jobs, moves every service to the images, smoke-tests the site and creates a GitHub release with the changes since the last tag.

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

For an actual recovery, Cloud SQL can also restore to any second within the backup window (point-in-time recovery), for example to just before a bad deploy:

```bash
gcloud sql instances clone prepza prepza-recovered --point-in-time="2026-10-02T12:00:00Z"
```

Then point `DATABASE_URL` at the clone, or copy the needed data back.

## Notes

- **Service addresses:** services reach each other at their Cloud Run addresses, which are known in advance (`https://<service>-<project number>.europe-west1.run.app`).
- **Who can call what:**
  - Public services take outside traffic only through the load balancer (ingress "internal and Cloud Load Balancing"), so Cloud Armor's rules always apply; their `run.app` addresses refuse the internet. The generation worker takes only Google's calls.
  - Calls between services go out through the private network in `network.tf` (Direct VPC egress, all traffic), so they arrive as internal; the internet (OpenAI, Resend, Paddle, Upstash) is reached through its Cloud NAT, about $1–5 a month at this size.
  - Calls between services also carry signed service tokens.
  - Pub/Sub, Cloud Tasks and Scheduler sign as the `prepza-invoker` account, which the services check.
- **Database users:** each service connects as its own Postgres user (named after its database) that owns only that database; other users can't even connect to it. The `prepza` user is the instance's admin and is used only by the `db-roles` job (`db_roles.tf`, `services/library/app/jobs/db_roles.py`), which creates those users and moves ownership to them. The deploy pipeline runs it before migrations; it's safe to repeat. **When first applying this over an existing database,** run it right after `terraform apply`, before any service restarts: `gcloud run jobs execute db-roles --region=europe-west1 --wait`. Until it has run, new instances can't connect, since their URLs already name the new users. Locally, Docker Compose keeps the one `prepza` user.
- **Least privilege:** each service runs as its own account (`prepza-<service>`, see `iam.tf`) that can read only its own secrets and its own database's URL. The frontend has no permissions; only the backend services publish events, and only the generation services queue tasks. Migrations run as their service's account. Applying this over the old shared `prepza-runtime` account moves every service to its own account, then deletes the old one.
- **App settings:** Terraform passes `DAILY_GENERATION_LIMIT` (from `daily_generation_limit`) but none of the other settings in `.env.example`: the AI models and reasoning efforts (`INTERVIEW_MODEL`, `VERIFY_MODEL`, `HELP_MODEL` and their `*_REASONING_EFFORT`), `INTERVIEW_QUESTIONS_PER_TOPIC`, `TEMPLATE_QUESTIONS_PER_TOPIC`, `MAX_TOPICS`, `MAX_SUBTOPICS`, `LLM_REQUESTS_PER_SECOND` and the per-user limits. The services run on their code defaults, which match `.env.example`. To change one in production, add it to the service's entry in `env.tf`.
- **Dead-lettered events:** an event a consumer failed on 50 times waits 7 days in the `events-dead-letter` subscription, and an alert emails you while any wait there. After fixing the consumer, replay them to the `events` topic with their attributes (the type), which acknowledges each one republished:

  ```bash
  # One at a time, so each is acknowledged well within the subscription's 10-second deadline.
  while m=$(gcloud pubsub subscriptions pull events-dead-letter --limit=1 --format=json | jq -c '.[0] // empty') && [ -n "$m" ]; do
    attrs=$(jq -r '.message.attributes | with_entries(select(.key | startswith("CloudPubSubDeadLetter") | not)) | to_entries | map("\(.key)=\(.value)") | join(",")' <<<"$m")
    gcloud pubsub topics publish events --message="$(jq -r .message.data <<<"$m" | base64 -d)" --attribute="$attrs" &&
      gcloud pubsub subscriptions ack events-dead-letter --ack-ids="$(jq -r .ackId <<<"$m")"
  done
  ```

  The replay goes to every consumer subscribed to that type, not only the one that failed: today each type has one consumer, but a type two consumers handle would reach the one that succeeded a second time.
- **Generation jobs:** a job may run up to 25 minutes, under Cloud Tasks' 30-minute limit. The queue tries a task up to 3 times (`jobs.tf`), for a delivery that fails before the job starts, such as a worker restarting; a job first moves its generation from queued to running in one atomic step, so a repeated delivery does nothing. A generation that fails once running is retried by the user.
- **Database connections:** Cloud SQL starts at `db-g1-small` with 200 connections allowed, 20 kept free. Each API process holds up to 10 connections (generation and the worker 14, notifications, ats and api 4); the services' `max` instances fit within the rest, and the plan fails if they don't (`database.tf`). Today that's at most 180 of the 180. A deploy briefly runs old and new instances side by side, so near the instance limits it can exceed the budget; this is accepted for launch, when services use a fraction of it (`internal_docs/code-review.md`, #32). Raise `db_tier` (and `db_max_connections`), or add PgBouncer, before allowing more instances or once services often run near their `max`.
- **High availability:** `db_high_availability = true` adds a standby in another zone, at about double the database cost.
- **Not yet tried on a real project:** `terraform validate` passes, but some settings may need a small adjustment on the first `apply`. The ones most likely to need it are the load balancer's backend protocol for Cloud Run, and Cloud Armor on the CDN backend.
