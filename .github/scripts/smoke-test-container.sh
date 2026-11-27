#!/usr/bin/env bash
# Smoke test for the pymzqc container images, run by the PR and release workflows
# before an image is pushed. Usage:
#   smoke-test-container.sh pymzqc IMAGE      library and CLI image (containers/Dockerfile)
#   smoke-test-container.sh validator IMAGE   online validator image
# Set DOCKER=podman to run it locally with podman.
set -euo pipefail

kind=$1
image=$2
docker=${DOCKER:-docker}

case "$kind" in
  pymzqc)
    "$docker" run --rm "$image" python -c \
      "from mzqc.MZQCFile import get_version_string; print('pymzqc', get_version_string())"
    for cmd in mzqc-validator mzqc-fileinfo mzqc-filemerger mzqc-fixdescriptions; do
      "$docker" run --rm "$image" "$cmd" --help > /dev/null
    done
    ;;
  validator)
    # Start the API the way compose.yaml and the README do.
    name="mzqc-validator-smoke-$$"
    port=5055
    "$docker" run -d --name "$name" -p "127.0.0.1:$port:5000" "$image" \
      python3 -m gunicorn mzqc_online_validator:app -b 0.0.0.0:5000 --chdir mzqc-validator/ > /dev/null
    cleanup() {
      status=$?
      if [ "$status" -ne 0 ]; then "$docker" logs "$name" || true; fi
      "$docker" rm -f "$name" > /dev/null 2>&1 || true
      exit "$status"
    }
    trap cleanup EXIT
    url="http://127.0.0.1:$port"
    for _ in $(seq 30); do
      curl -fsS "$url/status/" > /dev/null 2>&1 && break
      sleep 1
    done
    curl -fsS "$url/status/" | grep -q "API is running"
    curl -fsS "$url/documentation/" | grep -q '"version"'
    curl -fsS "$url/viewer/" | grep -q "<title>mzQC Viewer</title>"
    curl -fsS -o /dev/null "$url/viewer/mzqc-core.js"
    ;;
  *)
    echo "unknown image kind: $kind" >&2
    exit 2
    ;;
esac
echo "smoke test passed: $kind ($image)"
