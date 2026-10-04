#!/usr/bin/env bash
# Runs an offline test script inside a service container of the local stack, which has the
# service's code, packages and OpenAI key, then copies new datasets and results back.
#
#   evals/run.sh <generation|rounds> <script.py> [arguments]
#
# MODEL, EFFORT, JUDGE_MODEL and JUDGE_EFFORT are passed through when set.
set -euo pipefail

service="$1"
script="$2"
shift 2

here="$(cd "$(dirname "$0")" && pwd)"
container="prepza-${service}-1"

docker exec "$container" rm -rf /tmp/evals
docker cp "$here" "$container:/tmp/evals"

env_args=()

for name in MODEL EFFORT JUDGE_MODEL JUDGE_EFFORT; do
  if [[ -n "${!name:-}" ]]; then
    env_args+=(-e "$name=${!name}")
  fi
done

docker exec -w "/services/$service" -e "PYTHONPATH=/services/$service:/tmp/evals/scripts" \
  "${env_args[@]+"${env_args[@]}"}" "$container" \
  uv run --no-sync python "/tmp/evals/scripts/$script" "$@"

# Build scripts write datasets/; every script writes results/.
docker cp "$container:/tmp/evals/datasets/." "$here/datasets/"
docker cp "$container:/tmp/evals/results/." "$here/results/"
