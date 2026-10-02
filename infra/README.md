# Google Cloud infrastructure

Terraform for prepza on Google Cloud, in one region (`europe-west1`, Belgium) behind Google's global load balancer:

- **Cloud Run:** the frontend, five APIs, the generation worker and notifications. Billed per request, and idle services cost nothing.
- **Cloud SQL Postgres 17:** one database per service, with daily backups and point-in-time recovery.
- **Pub/Sub:** domain events. One `events` topic is pushed to library, companies and notifications, with a dead-letter topic after 5 attempts.
- **Cloud Tasks:** generation jobs on the worker. **Cloud Scheduler:** sweeps and retention.
- **The global load balancer:**
  - HTTPS with a Google-managed certificate;
  - `/api/<service>/` routes to each API, and everything else to the frontend;
  - Cloud CDN for static files;
  - a Cloud Armor rule that blocks `/api/*/internal/`.
- **Secret Manager** for secrets, and **Artifact Registry** for images.

Outside Google Cloud: Redis on **Upstash** (rate limits, the LLM limiter, the draft cache), **Firebase Authentication** (same project), **Resend**, **Sentry** and **Paddle**.

## Bootstrap (once)

You need `gcloud`, Docker and Terraform 1.9+ (or `docker run hashicorp/terraform`).

1. **Create the project and link billing.**
   ```bash
   gcloud projects create prepza-prod
   gcloud billing projects link prepza-prod --billing-account=<BILLING_ACCOUNT_ID>
   gcloud config set project prepza-prod
   gcloud auth application-default login
   ```
2. **Add Firebase to the project** in the [Firebase console](https://console.firebase.google.com) ("Add project", then choose `prepza-prod`).
   - **Authentication → Sign-in method:** enable Google.
   - **Authentication → Settings → Authorized domains:** add `prepza.ai`.
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
6. **Create the image registry first,** then push the first images. The deploy pipeline does this on every push afterwards.
   - Cloud Run runs `linux/amd64`, so build for it even on an Apple-silicon Mac.
   - Use the same tag as `image_tag` in `terraform.tfvars`.

   ```bash
   terraform apply -target=google_artifact_registry_repository.images
   gcloud auth configure-docker europe-west1-docker.pkg.dev
   REGISTRY=europe-west1-docker.pkg.dev/prepza-prod/prepza
   for service in library generation rounds companies billing notifications; do
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
   printf '%s' "$PADDLE_WEBHOOK_SECRET" | gcloud secrets versions add paddle-webhook-secret --data-file=-
   ```

   Services read `latest` when they start, so redeploy (step 9) after setting secrets.
9. **Run the migrations, then restart the services** so they pick up the secrets.
   ```bash
   for db in library generation rounds companies billing; do
     gcloud run jobs execute $db-migrate --region=europe-west1 --wait
   done
   # A new revision of each service reads the secrets you just set.
   for service in frontend library generation rounds companies billing notifications generation-worker; do
     gcloud run services update $service --region=europe-west1 --update-labels=restarted=$(date +%s)
   done
   ```
10. **Point the domain at the load balancer.** In GoDaddy's DNS, add an **A record** for `@` with the value of `terraform output site_ip`. Google then issues the certificate, which can take up to about an hour:
    ```bash
    gcloud compute ssl-certificates describe prepza --global --format='value(managed.status)'
    ```
11. **Update the services that call back to the site:**
    - **Paddle:** the webhook destination is `https://prepza.ai/api/billing/webhooks/paddle`.
    - **Resend:** the `prepza.ai` sending domain is already verified.
    - **Sentry:** set `sentry_dsn` in `terraform.tfvars`.

12. **Connect GitHub for deploys.** In the repository's **Settings → Secrets and variables → Actions → Variables**, add:
    - **From Terraform:** everything in `terraform output github_variables`, which gives `GCP_PROJECT_ID`, `GCP_REGION`, `GCP_WORKLOAD_IDENTITY_PROVIDER`, `GCP_DEPLOY_SERVICE_ACCOUNT` and `SITE_URL`.
    - **From Firebase:** `NEXT_PUBLIC_FIREBASE_API_KEY` and `NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN`, from the web app in step 2.
    - **Optionally:** `NEXT_PUBLIC_SENTRY_DSN` for the frontend.

    These are variables, not secrets: none of them grants access. GitHub's signed token is what lets the pipeline in, and only for `main` of this repository.

## Deploys

Every push to `main` that passes CI deploys through [`.github/workflows/deploy.yml`](../.github/workflows/deploy.yml):
1. Builds the 7 images for `linux/amd64`, tagged with the commit.
2. Runs the 5 migration jobs.
3. Moves every service to the new images.
4. Smoke-tests the site.

A failed step stops the deploy, and the services keep running the previous images.

- **Rolling back:** move a service to an earlier revision in the Cloud Run console, or rerun the workflow for an earlier commit.
- **Terraform never touches image tags,** so applying an infrastructure change doesn't roll anything back.

## Restore drill

A backup is only proven by restoring it. Run `scripts/restore-drill.sh prepza-prod` before launch, and then every quarter. It needs `gcloud`, `cloud-sql-proxy` and `psql`, and it:
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
  - Public services accept everyone and check users themselves.
  - Calls between services carry signed service tokens.
  - Pub/Sub, Cloud Tasks and Scheduler sign as the `prepza-invoker` account, which the services check.
- **Generation jobs:** a job may run up to 25 minutes, under Cloud Tasks' 30-minute limit. The queue never retries; a failed generation is retried by the user.
- **Database connections:** Cloud SQL starts at `db-g1-small` with 200 connections allowed. Each API process holds up to 10 connections, so raise `db_tier`, or add PgBouncer, before allowing many instances.
- **High availability:** `db_high_availability = true` adds a standby in another zone, at about double the database cost.
- **Not yet tried on a real project:** `terraform validate` passes, but some settings may need a small adjustment on the first `apply`. The ones most likely to need it are the load balancer's backend protocol for Cloud Run, and Cloud Armor on the CDN backend.
