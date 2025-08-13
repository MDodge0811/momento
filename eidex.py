import sqlite3
import os
import json
import argparse
import sys
from datetime import datetime, timedelta
from git import Repo, GitCommandError


def get_repo_root():
    """Get the root directory of the current Git repo."""
    try:
        repo = Repo(search_parent_directories=True)
        return repo.working_dir
    except GitCommandError:
        raise ValueError(
            "Not in a Git repository. Momento requires a Git repo to store logs."
        )


def get_db_path():
    """Get the path to the repo-specific SQLite DB."""
    repo_root = get_repo_root()
    return os.path.join(repo_root, ".eidex-logs.db")


def ensure_db():
    """Initialize SQLite DB with table and indexes, add to .gitignore."""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            branch TEXT NOT NULL,
            message TEXT NOT NULL,
            extra TEXT
        )
    """
    )
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_branch_timestamp ON logs (branch, timestamp)"
    )
    conn.commit()
    conn.close()

    # Add to .gitignore
    gitignore_path = os.path.join(get_repo_root(), ".gitignore")
    db_path_relative = ".eidex-logs.db"
    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r+") as f:
            content = f.read()
            if db_path_relative not in content:
                f.write(f"\n{db_path_relative}\n")
    else:
        with open(gitignore_path, "w") as f:
            f.write(f"{db_path_relative}\n")


def get_current_branch():
    """Get the current Git branch or raise an error if not in a repo."""
    try:
        repo = Repo(search_parent_directories=True)
        return repo.active_branch.name
    except GitCommandError:
        raise ValueError("Not in a Git repository. Eidex requires a Git repo.")


def log_work(message: str, extra_info: dict = None):
    """Log an AI action for the current branch."""
    ensure_db()
    branch = get_current_branch()
    extra_json = json.dumps(extra_info) if extra_info else None
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO logs (branch, message, extra) VALUES (?, ?, ?)",
        (branch, message, extra_json),
    )
    conn.commit()
    conn.close()


def fetch_branch_logs(branch: str = None, limit: int = 50) -> list[dict]:
    """Fetch logs for the current or specified branch, newest first."""
    ensure_db()
    if branch is None:
        branch = get_current_branch()

    # Validate limit parameter
    if limit <= 0:
        return []

    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT timestamp, branch, message, extra
        FROM logs
        WHERE branch = ?
        ORDER BY timestamp DESC
        LIMIT ?
    """,
        (branch, limit),
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "timestamp": row[0],
            "branch": row[1],
            "message": row[2],
            "extra": json.loads(row[3]) if row[3] else None,
        }
        for row in rows
    ]


def cleanup_deleted_branches():
    """Delete logs for branches that no longer exist."""
    ensure_db()
    repo = Repo(search_parent_directories=True)
    existing_branches = {b.name for b in repo.branches}
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT branch FROM logs")
    logged_branches = {row[0] for row in cursor.fetchall()}
    for branch in logged_branches:
        if branch not in existing_branches:
            cursor.execute("DELETE FROM logs WHERE branch = ?", (branch,))
    conn.commit()
    conn.close()


def prune_old_logs(days: int) -> int:
    """Delete logs older than the specified number of days."""
    ensure_db()
    cutoff = (datetime.now() - timedelta(days=days)).isoformat()
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute("DELETE FROM logs WHERE timestamp < ?", (cutoff,))
    deleted_count = cursor.rowcount
    conn.commit()
    conn.close()
    return deleted_count


def main():
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
        "--limit", type=int, help="Max logs to return", default=50
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

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
