#!/usr/bin/env bash
set -euo pipefail

repo_root="$(git rev-parse --show-toplevel)"
output_dir="${M00_OUTPUT_DIR:-artifacts/verification/milestone-00-main}"
run_label="${M00_RUN_LABEL:-main}"
project_name="${COMPOSE_PROJECT_NAME:-jobseeker_m00_main}"

while (($#)); do
    case "$1" in
        --output-dir)
            output_dir="$2"
            shift 2
            ;;
        --project-name)
            project_name="$2"
            shift 2
            ;;
        --run-label)
            run_label="$2"
            shift 2
            ;;
        *)
            echo "unknown argument: $1" >&2
            exit 2
            ;;
    esac
done

case "$output_dir" in
    /*) ;;
    *) output_dir="$repo_root/$output_dir" ;;
esac

export COMPOSE_PROJECT_NAME="$project_name"
mkdir -p "$output_dir/logs"
manifest="$output_dir/manifest.tsv"
metadata="$output_dir/metadata.tsv"
tested_commit="$(git rev-parse HEAD)"
image_digest=""

printf 'gate_id\tcommand\texit_code\tduration_seconds\tlog_ref\ttest_count\tresult\n' >"$manifest"

reference_for() {
    local path="$1"
    case "$path" in
        "$repo_root"/*) printf '%s' "${path#"$repo_root"/}" ;;
        *) printf '%s' "$path" ;;
    esac
}

write_metadata() {
    local result="$1"
    {
        printf 'key\tvalue\n'
        printf 'schema_version\t1\n'
        printf 'run_label\t%s\n' "$run_label"
        printf 'tested_commit\t%s\n' "$tested_commit"
        printf 'timestamp_utc\t%s\n' "$(date -u +'%Y-%m-%dT%H:%M:%SZ')"
        printf 'compose_project_name\t%s\n' "$project_name"
        printf 'image_digest\t%s\n' "$image_digest"
        printf 'result\t%s\n' "$result"
    } >"$metadata"
}

run_gate() {
    local gate_id="$1"
    local expects_tests="$2"
    shift 2
    local log="$output_dir/logs/${gate_id}.log"
    local log_ref
    local command_text
    local start
    local finish
    local duration
    local exit_code
    local test_count=""
    local result="PASS"

    printf -v command_text '%q ' "$@"
    command_text="${command_text% }"
    start="$(date +%s)"
    set +e
    "$@" >"$log" 2>&1
    exit_code=$?
    set -e
    finish="$(date +%s)"
    duration=$((finish - start))
    cat "$log"

    if [[ "$expects_tests" == "yes" ]]; then
        test_count="$(grep -Eo '[0-9]+ passed' "$log" | tail -n 1 | sed 's/ passed//' || true)"
        test_count="${test_count:-0}"
    fi
    if ((exit_code != 0)) || { [[ "$expects_tests" == "yes" ]] && ((test_count <= 0)); }; then
        result="FAIL"
    fi
    log_ref="$(reference_for "$log")"
    printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
        "$gate_id" "$command_text" "$exit_code" "$duration" "$log_ref" "$test_count" "$result" \
        >>"$manifest"

    if [[ "$result" != "PASS" ]]; then
        write_metadata "FAIL"
        if ((exit_code != 0)); then
            return "$exit_code"
        fi
        return 96
    fi
}

run_gate 01-compose-config no docker compose --profile dev config --quiet || exit $?
run_gate 02-build-api no docker compose --profile dev build api || exit $?
run_gate 03-image-digest no docker image inspect "${project_name}-api" --format '{{.Id}}' || exit $?
image_digest="$(tail -n 1 "$output_dir/logs/03-image-digest.log")"
run_gate 04-validate-docs no \
    docker compose --profile dev run --rm --no-deps api python scripts/validate_docs.py || exit $?
run_gate 05-validate-milestone no \
    docker compose --profile dev run --rm --no-deps api \
    python scripts/validate_milestone.py --all || exit $?
run_gate 06-validate-codex-controls no \
    docker compose --profile dev run --rm --no-deps api \
    python scripts/validate_codex_controls.py || exit $?
run_gate 07-ruff no docker compose --profile dev run --rm --no-deps api ruff check . || exit $?
run_gate 08-mypy no docker compose --profile dev run --rm --no-deps api mypy src || exit $?
run_gate 09-pytest yes docker compose --profile dev run --rm --no-deps api pytest -q || exit $?
run_gate 10-pre-commit no \
    docker compose --profile dev run --rm --no-deps api sh -c \
    'git config --global --add safe.directory /app && pre-commit run --all-files' || exit $?

write_metadata "PASS"
