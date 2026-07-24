#!/usr/bin/env bash
set -euo pipefail

validate_reference_dir() {
    local value="$1"
    local segment
    local -a segments
    if [[ -z "$value" || "$value" == /* || "$value" == *$'\t'* || "$value" == *$'\n'* ]]; then
        echo "reference directory must be a nonempty repository-relative path" >&2
        return 2
    fi
    IFS='/' read -r -a segments <<<"$value"
    for segment in "${segments[@]}"; do
        if [[ "$segment" == ".." ]]; then
            echo "reference directory must not contain '..' traversal" >&2
            return 2
        fi
    done
}

reference_for() {
    local physical_path="$1"
    local gate_id="$2"
    if [[ "$reference_dir_set" == "true" ]]; then
        printf '%s/logs/%s.log' "${reference_dir%/}" "$gate_id"
        return
    fi
    case "$physical_path" in
        "$repo_root"/*) printf '%s' "${physical_path#"$repo_root"/}" ;;
        *) printf '%s' "$physical_path" ;;
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
    log_ref="$(reference_for "$log" "$gate_id")"
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

capture_clean_checkout() {
    local status_log="$output_dir/checkout-status.log"
    local status_exit
    set +e
    git status --porcelain >"$status_log"
    status_exit=$?
    set -e
    if ((status_exit != 0)); then
        echo "clean-checkout Git status failed with exit $status_exit" >&2
        return "$status_exit"
    fi
    if [[ -s "$status_log" ]]; then
        echo "clean checkout contains generated or modified files:" >&2
        cat "$status_log" >&2
        return 97
    fi
}

validate_run_label() {
    case "$run_label" in
        main|clean|preflight) ;;
        *)
            echo "run label must be one of: main, clean, preflight" >&2
            return 2
            ;;
    esac
}

require_clean_source_tree() {
    if [[ "$run_label" == "preflight" ]]; then
        return
    fi

    local source_status
    local status_exit
    set +e
    source_status="$(git status --porcelain --untracked-files=all)"
    status_exit=$?
    set -e
    if ((status_exit != 0)); then
        echo "source-tree Git status failed with exit $status_exit" >&2
        return "$status_exit"
    fi
    if [[ -n "$source_status" ]]; then
        echo "$run_label evidence requires a clean source tree before gates run:" >&2
        printf '%s\n' "$source_status" >&2
        return 97
    fi
}

main() {
    output_dir="${M03_OUTPUT_DIR:-artifacts/verification/milestone-03-main}"
    run_label="${M03_RUN_LABEL:-main}"
    project_name="${COMPOSE_PROJECT_NAME:-jobseeker_m03_main}"
    reference_dir=""
    reference_dir_set="false"

    while (($#)); do
        case "$1" in
            --output-dir)
                (($# >= 2)) || { echo "--output-dir requires a value" >&2; return 2; }
                output_dir="$2"
                shift 2
                ;;
            --reference-dir)
                (($# >= 2)) || { echo "--reference-dir requires a value" >&2; return 2; }
                reference_dir="$2"
                reference_dir_set="true"
                shift 2
                ;;
            --project-name)
                (($# >= 2)) || { echo "--project-name requires a value" >&2; return 2; }
                project_name="$2"
                shift 2
                ;;
            --run-label)
                (($# >= 2)) || { echo "--run-label requires a value" >&2; return 2; }
                run_label="$2"
                shift 2
                ;;
            *)
                echo "unknown argument: $1" >&2
                return 2
                ;;
        esac
    done

    if [[ "$reference_dir_set" == "true" ]]; then
        validate_reference_dir "$reference_dir"
    fi
    validate_run_label
    repo_root="$(git rev-parse --show-toplevel)"
    case "$output_dir" in
        /*) ;;
        *) output_dir="$repo_root/$output_dir" ;;
    esac

    require_clean_source_tree

    export COMPOSE_PROJECT_NAME="$project_name"
    mkdir -p "$output_dir/logs"
    manifest="$output_dir/manifest.tsv"
    metadata="$output_dir/metadata.tsv"
    tested_commit="$(git rev-parse HEAD)"
    image_digest=""

    printf 'gate_id\tcommand\texit_code\tduration_seconds\tlog_ref\ttest_count\tresult\n' \
        >"$manifest"

    run_gate 01-compose-config no docker compose --profile dev config --quiet || return $?
    run_gate 02-build-api no docker compose --profile dev build api || return $?
    run_gate 03-image-digest no \
        docker image inspect "${project_name}-api" --format '{{.Id}}' || return $?
    image_digest="$(tail -n 1 "$output_dir/logs/03-image-digest.log")"
    run_gate 04-profile-validate no \
        docker compose --profile dev run --rm --no-deps api \
        job-agent profile-validate || return $?
    run_gate 05-validate-docs no \
        docker compose --profile dev run --rm --no-deps api \
        python scripts/validate_docs.py || return $?
    run_gate 06-validate-milestone no \
        docker compose --profile dev run --rm --no-deps api \
        python scripts/validate_milestone.py --all || return $?
    run_gate 07-validate-codex-controls no \
        docker compose --profile dev run --rm --no-deps api \
        python scripts/validate_codex_controls.py || return $?
    run_gate 08-ruff no \
        docker compose --profile dev run --rm --no-deps api ruff check . || return $?
    run_gate 09-mypy no \
        docker compose --profile dev run --rm --no-deps api mypy src || return $?
    run_gate 10-pytest yes \
        docker compose --profile dev run --rm --no-deps api pytest -q || return $?
    run_gate 11-pre-commit no \
        docker compose --profile dev run --rm --no-deps api sh -c \
        'git config --global --add safe.directory /app && pre-commit run --all-files' || return $?

    if [[ "$run_label" == "clean" ]]; then
        local checkout_exit
        set +e
        capture_clean_checkout
        checkout_exit=$?
        set -e
        if ((checkout_exit != 0)); then
            write_metadata "FAIL"
            return "$checkout_exit"
        fi
    fi

    write_metadata "PASS"
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
    main "$@"
fi
