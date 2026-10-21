#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."

mkdir -p .wsl-runs
demo_run=$(mktemp -d .wsl-runs/live-XXXXXX)
demo_root="$demo_run/service"
mkdir "$demo_root"
git archive HEAD target-service | tar -x --strip-components=1 \
  --exclude='target-service/tests/test_student.py' -C "$demo_root"
cp checks/fixtures/pricing_baseline.py "$demo_root/orders/pricing.py"

git -C "$demo_root" init --initial-branch=main
git -C "$demo_root" add .
git -C "$demo_root" -c user.name="Lab Student" -c user.email="student@example.invalid" \
  commit -m "Record original pricing baseline"

printf '%s\n' "$demo_root" > .wsl-runs/current-demo.txt
printf 'Demo-Verzeichnis: %s\n' "$demo_root"
