"""Command-line interface for Eidex."""

import argparse
import json
import sys

from .database import (
    cleanup_deleted_branches,
    fetch_branch_logs,
    log_work,
    prune_old_logs,
)
from .config import load_config
from .file_generators import create_default_config, create_ai_context_file


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Eidex: Branch-aware AI logging")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # log_work command
    log_parser = subparsers.add_parser("log_work", help="Log an AI action")
    log_parser.add_argument("message", help="Log message")
    log_parser.add_argument(
        "--extra",
        help='JSON string of extra info, e.g., --extra \'{"key": "value"}\'',
        default=None,
    )

    # fetch_branch_logs command
    fetch_parser = subparsers.add_parser("fetch_branch_logs", help="Fetch branch logs")
    fetch_parser.add_argument(
        "--branch", help="Branch name (default: current)", default=None
    )
    fetch_parser.add_argument(
        "--limit", type=int, help="Max logs to return", default=None
    )

    # cleanup_deleted_branches command
    subparsers.add_parser(
        "cleanup_deleted_branches", help="Delete logs for non-existent branches"
    )

    # prune_old_logs command
    prune_old_parser = subparsers.add_parser(
        "prune_old_logs", help="Delete logs older than X days"
    )
    prune_old_parser.add_argument("days", type=int, help="Days to keep")

    # show_config command
    subparsers.add_parser("show_config", help="Show current configuration")

    # init_config command
    subparsers.add_parser("init_config", help="Create or recreate configuration file")

    # create_context command
    subparsers.add_parser("create_context", help="Create or recreate AI context file")

    try:
        args = parser.parse_args()
    except SystemExit:
        if "log_work" in sys.argv:
            print(
                'Error: Invalid arguments. Use: eidex log_work "string" --extra valid_python_dict, e.g., --extra \'{"key": "value"}\'',
                file=sys.stderr,
            )
        else:
            print(
                "Error: Invalid arguments. Use: eidex <command> [options]. Run 'eidex --help' for details.",
                file=sys.stderr,
            )
        sys.exit(1)

    try:
        if args.command == "log_work":
            extra_info = None
            if args.extra:
                try:
                    extra_info = json.loads(args.extra)
                except json.JSONDecodeError:
                    raise ValueError(
                        'The --extra flag must be a valid JSON string, e.g., --extra \'{"key": "value"}\''
                    )
            log_work(args.message, extra_info)
            print(f"Logged: {args.message}")
        elif args.command == "fetch_branch_logs":
            logs = fetch_branch_logs(args.branch, args.limit)
            print(json.dumps(logs, indent=2))
        elif args.command == "cleanup_deleted_branches":
            cleanup_deleted_branches()
            print("Cleaned up logs for deleted branches.")
        elif args.command == "prune_old_logs":
            deleted = prune_old_logs(args.days)
            print(f"Deleted {deleted} logs older than {args.days} days.")
        elif args.command == "show_config":
            config = load_config()
            print("Current Eidex Configuration:")
            print(json.dumps(config, indent=2))
        elif args.command == "init_config":
            create_default_config()
        elif args.command == "create_context":
            context_path = create_ai_context_file()
            print(f"AI context file created: {context_path}")
            print(
                "AI agents can now reference this file for comprehensive usage instructions."
            )

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
