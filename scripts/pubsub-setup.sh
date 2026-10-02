#!/bin/sh
# Creates the local Pub/Sub topic and its push subscriptions in the emulator, as Terraform does in
# Google Cloud. Safe to repeat: existing ones answer 409 and are left as they are.
set -eu

base="http://${PUBSUB_EMULATOR_HOST}/v1/projects/${GOOGLE_CLOUD_PROJECT}"

until curl -sf "http://${PUBSUB_EMULATOR_HOST}/" >/dev/null; do
  sleep 1
done

curl -s -o /dev/null -X PUT "$base/topics/events"

for consumer in library companies notifications; do
  curl -s -o /dev/null -X PUT "$base/subscriptions/$consumer-events" \
    -H "Content-Type: application/json" \
    -d "{\"topic\": \"projects/${GOOGLE_CLOUD_PROJECT}/topics/events\",
         \"pushConfig\": {\"pushEndpoint\": \"http://$consumer:8000/internal/events\"}}"
done

echo "pubsub ready"
