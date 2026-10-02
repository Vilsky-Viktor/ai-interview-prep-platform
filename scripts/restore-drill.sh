#!/usr/bin/env bash
# Proves backups restore: the latest backup goes into a temporary Cloud SQL instance, its main
# tables are counted, and the instance is deleted. Run before launch, then quarterly.
# Needs gcloud (signed in), cloud-sql-proxy and psql. Usage: scripts/restore-drill.sh prepza-prod
set -euo pipefail

project="${1:?usage: scripts/restore-drill.sh <project id>}"
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

gcloud sql instances create "$drill" --project="$project" --region="$region" \
  --database-version=POSTGRES_17 --edition=ENTERPRISE --tier=db-g1-small --no-backup --quiet
gcloud sql backups restore "$backup" --project="$project" --backup-instance="$source_instance" \
  --restore-instance="$drill" --quiet

# The restored instance has the source's users, so the app's own password works.
url=$(gcloud secrets versions access latest --secret=database-url-library --project="$project")
password=$(sed -E 's|postgresql://prepza:([^@]+)@.*|\1|' <<<"$url")

cloud-sql-proxy --port "$port" "$project:$region:$drill" &
proxy=$!
sleep 5

count() {
  PGPASSWORD="$password" psql -h 127.0.0.1 -p "$port" -U prepza -d "$1" -tAc "SELECT count(*) FROM $2"
}

echo "library:     $(count library sets) sets, $(count library questions) questions"
echo "rounds:      $(count rounds rounds) rounds, $(count rounds answers) answers"
echo "companies:   $(count companies companies) companies, $(count companies candidate_invites) invites"
echo "generation:  $(count generation generations) generations"
echo "billing:     $(count billing purchases) purchases"
echo "Restore drill passed: the backup restores and its data reads back."
