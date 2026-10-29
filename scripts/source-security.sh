#!/usr/bin/env bash
set -euo pipefail
repository="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
report_directory="${1:-$repository/.security-reports}"
if [[ "$#" -gt 1 ]]; then
  printf 'Usage: source-security.sh [report-directory]\n' >&2
  exit 2
fi
mkdir -p "$report_directory"
report_directory="$(cd "$report_directory" && pwd)"
scan_directory="$(mktemp -d)"
trivy_cache_directory="$(mktemp -d "$repository/.source-security-cache.XXXXXXXX")"
trivy_image="aquasec/trivy@sha256:62b1e65e8869bc4b4c6aa4fa2b21595256c7c2f6018a9d9ad61caf87187c1969"
scanner_user="$(id -u):$(id -g)"
trap 'rm -rf "$scan_directory" "$trivy_cache_directory"' EXIT
# Only committed public source is scanned. Local credentials/private QA are absent.
git -C "$repository" archive HEAD | tar -x -C "$scan_directory"
inventory_python="${RAGWELL_SECURITY_PYTHON:-python3}"
if [[ -z "${RAGWELL_SECURITY_PYTHON:-}" && -x "$repository/.venv/bin/python" ]]; then
  inventory_python="$repository/.venv/bin/python"
fi
"$inventory_python" - "$scan_directory" "$report_directory" <<'PY'
import json
import sys
import tomllib
from pathlib import Path

source, reports = map(Path, sys.argv[1:])
with (source / "uv.lock").open("rb") as stream:
    packages = tomllib.load(stream)["package"]
with (source / "pyproject.toml").open("rb") as stream:
    project_name = tomllib.load(stream)["project"]["name"]
inventory = sorted(
    {(package["name"], package["version"]) for package in packages if package["name"] != project_name}
)
directory = source / "all-locked-dependencies"
directory.mkdir()
(directory / "requirements.txt").write_text(
    "".join(f"{name}=={version}\n" for name, version in inventory), encoding="utf-8"
)
(reports / "locked-inventory.json").write_text(
    json.dumps([{"name": name, "version": version} for name, version in inventory], indent=2) + "\n",
    encoding="utf-8",
)
PY
printf '{"source_commit":"%s"}\n' "$(git -C "$repository" rev-parse HEAD)" \
  > "$report_directory/source.json"
docker run --rm --memory 768m --cpus 1 --pids-limit 256 --network none \
  -v "$scan_directory:/src:ro" -v "$report_directory:/reports" \
  zricethezav/gitleaks@sha256:c00b6bd0aeb3071cbcb79009cb16a60dd9e0a7c60e2be9ab65d25e6bc8abbb7f \
  dir /src --redact=100 --no-banner --report-format json --report-path /reports/secrets.json
docker_security_options="$(docker info --format '{{json .SecurityOptions}}')"
if [[ "$docker_security_options" == *rootless* ]]; then
  scanner_user="0:0"
fi
# Public advisory downloads have no repository mount; source scans have no network.
docker run --rm --memory 768m --cpus 1 --pids-limit 256 --user "$scanner_user" \
  -v "$trivy_cache_directory:/cache" "$trivy_image" \
  fs --download-db-only --cache-dir /cache --no-progress --disable-telemetry
docker run --rm --memory 768m --cpus 1 --pids-limit 256 --user "$scanner_user" --network none \
  -v "$scan_directory:/src:ro" -v "$trivy_cache_directory:/cache" -v "$report_directory:/reports" \
  "$trivy_image" fs --cache-dir /cache --offline-scan --skip-db-update --skip-java-db-update \
  --disable-telemetry --scanners vuln,license --include-dev-deps --license-full --format cyclonedx \
  --output /reports/sbom.cdx.json /src
docker run --rm --memory 768m --cpus 1 --pids-limit 256 --user "$scanner_user" --network none \
  -v "$scan_directory:/src:ro" -v "$trivy_cache_directory:/cache" -v "$report_directory:/reports" \
  "$trivy_image" fs --cache-dir /cache --offline-scan --skip-db-update --skip-java-db-update \
  --disable-telemetry --scanners vuln,license --include-dev-deps --license-full --format json \
  --output /reports/dependencies-and-licenses.json --severity HIGH,CRITICAL --exit-code 1 /src
