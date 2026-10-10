#!/usr/bin/env bash
# Proves backups restore: the latest backup goes into a temporary Cloud SQL instance, its main
# tables are counted, and the instance is deleted. Run before launch, then quarterly.
# Needs gcloud (signed in), cloud-sql-proxy and psql. Usage: scripts/ops/restore-drill.sh prepza-prod
set -euo pipefail

project="${1:?usage: scripts/ops/restore-drill.sh <project id>}"
region="${REGION:-europe-west1}"
source_instance="prepza"
drill="prepza-restore-drill-$(date +%Y%m%d%H%M)"
port=6543

cleanup() {
  [[ -n "${proxy:-}" ]] && kill "$proxy" 2>/dev/null || true
  echo "Deleting $drill"
  gcloud sql instances delete "$drill" --project="$project" --quiet || true
}
trap cleanup EXIT

backup=$(gcloud sql backups list --instance="$source_instance" --project="$project" \
  --filter="status=SUCCESSFUL" --sort-by=~endTime --limit=1 --format="value(id)")
echo "Restoring backup $backup into $drill"

# The drill instance runs the source's Postgres version, or the restore is refused.
version=$(gcloud sql instances describe "$source_instance" --project="$project" \
  --format="value(databaseVersion)")
gcloud sql instances create "$drill" --project="$project" --region="$region" \
  --database-version="$version" --edition=ENTERPRISE --tier=db-g1-small --no-backup --quiet
gcloud sql backups restore "$backup" --project="$project" --backup-instance="$source_instance" \
  --restore-instance="$drill" --quiet

# The restored instance has the source's users. The admin (prepza) holds every service's role
# (db_roles.py), so it reads every database.
url=$(gcloud secrets versions access latest --secret=database-admin-url --project="$project")
password=$(sed -E 's|postgresql://prepza:([^@]+)@.*|\1|' <<<"$url")

cloud-sql-proxy --port "$port" "$project:$region:$drill" &
proxy=$!
sleep 5

# One table of each service's database. A failed count stops the drill: each runs in its own
# assignment, so `set -e` sees it.
checks=(
  "library sets"
  "library questions"
  "rounds sessions"
  "rounds answers"
  "companies companies"
  "companies candidate_invites"
  "generation generations"
  "billing entries"
  "notifications notifications"
  "ats ats_connections"
  "api api_keys"
  "assistant conversations"
)

for check in "${checks[@]}"; do
  read -r database table <<<"$check"
  rows=$(PGPASSWORD="$password" psql -h 127.0.0.1 -p "$port" -U prepza -d "$database" \
    -v ON_ERROR_STOP=1 -tAc "SELECT count(*) FROM $table")
  printf '%-14s %-20s %s rows\n' "$database" "$table" "$rows"
done

echo "Restore drill passed: the backup restores and every database reads back."
