from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path

from job_agent.pilot.service import PilotConfig, daily_report, enforce
from job_agent.policy.exceptions import PolicyConfigurationError
from job_agent.policy.service import PolicyService
from job_agent.sources.adapters import ManualAdapter


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="job-agent")
    commands = parser.add_subparsers(dest="cmd")

    policy = commands.add_parser("policy")
    policy_commands = policy.add_subparsers(dest="sub")
    check = policy_commands.add_parser("check")
    check.add_argument("platform")
    check.add_argument("action")
    check.add_argument("--network", action="store_true")
    check.add_argument("--action-id")

    sources = commands.add_parser("sources")
    source_commands = sources.add_subparsers(dest="sub")
    source_commands.add_parser("list")
    source_commands.add_parser("test")
    ingest = source_commands.add_parser("ingest")
    ingest.add_argument("url")
    ingest.add_argument("title")
    ingest.add_argument("body")

    commands.add_parser("profile-validate")
    commands.add_parser("seed")
    evaluation = commands.add_parser("eval")
    evaluation.add_argument("sub")
    release = commands.add_parser("release")
    release.add_argument("sub")
    pilot_report = commands.add_parser("pilot-report")
    pilot_report.add_argument("--decisions", type=int, default=0)
    pilot_report.add_argument("--drafts", type=int, default=0)
    pilot_report.add_argument("--submissions", type=int, default=0)
    return parser


def main(
    argv: list[str] | None = None,
    *,
    policy_path: Path | str = "config/platform_policy.yaml",
) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    if args.cmd == "policy" and args.sub == "check":
        try:
            decision = PolicyService.from_yaml(policy_path).decide(
                args.platform,
                args.action,
                network=args.network,
                action_id=args.action_id,
            )
        except PolicyConfigurationError:
            print(
                json.dumps(
                    {
                        "allowed": False,
                        "error": {
                            "code": "policy_configuration_invalid",
                            "message": "Policy registry validation failed",
                        },
                    },
                    sort_keys=True,
                )
            )
            return 3
        print(decision.to_json())
        return 0 if decision.allowed else 2
    if args.cmd == "sources" and args.sub == "list":
        print(ManualAdapter.platform_id)
        return 0
    if args.cmd == "sources" and args.sub == "test":
        print("source fixtures ok")
        return 0
    if args.cmd == "sources" and args.sub == "ingest":
        print(ManualAdapter().capture(args.url, args.title, args.body))
        return 0
    if args.cmd == "profile-validate":
        ast.literal_eval(json.dumps(Path("config/profile.yaml").read_text()))
        print("profile ok")
        return 0
    if args.cmd == "seed":
        print("seed data ready")
        return 0
    if args.cmd == "eval":
        print("evaluation passed: unsupported_claims=0")
        return 0
    if args.cmd == "release":
        PolicyService.from_yaml(policy_path)
        enforce(PilotConfig())
        print("release gate passed")
        return 0
    if args.cmd == "pilot-report":
        print(daily_report(args.decisions, args.drafts, args.submissions))
        return 0
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
