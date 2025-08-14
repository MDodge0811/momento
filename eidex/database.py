"""Database operations for Eidex."""

import json
import os
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Any

from .config import get_config_value, get_repo_root
from .file_generators import ensure_eidex_directory


def get_db_path() -> str:
    """Get the path to the repo-specific SQLite DB."""
    repo_root = get_repo_root()
    db_filename = get_config_value("database", "filename", ".eidex-logs.db")
    return f"{repo_root}/.eidex/{db_filename}"


def ensure_db() -> str:
    """Initialize SQLite DB with table and indexes, add to .gitignore."""
    # Ensure .eidex directory exists
    ensure_eidex_directory()

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

    # Add to .gitignore if configured to do so
    if get_config_value("git", "auto_add_to_gitignore", True):
        gitignore_path = f"{get_repo_root()}/.gitignore"
        gitignore_entries = get_config_value("git", "gitignore_entries", [".eidex/"])

        if os.path.exists(gitignore_path):
            with open(gitignore_path, "r+") as f:
                content = f.read()
                for entry in gitignore_entries:
                    if entry not in content:
                        f.write(f"\n{entry}\n")
        else:
            with open(gitignore_path, "w") as f:
                for entry in gitignore_entries:
                    f.write(f"{entry}\n")

    return db_path


def log_work(message: str, extra_info: Dict[str, Any] = None) -> None:
    """Log an AI action for the current branch.
    
    Args:
        message: Description of the AI action performed
        extra_info: Optional structured data about the action
        
    Returns:
        None (logs are stored in the database)
        
    Note:
        This function automatically ensures the database exists and handles
        cleanup of old logs based on configuration settings.
    """
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

    # Auto-cleanup old logs if configured
    if get_config_value("database", "auto_cleanup_old_logs", True):
        cleanup_threshold = get_config_value("database", "cleanup_days_threshold", 90)
        try:
            prune_old_logs(cleanup_threshold)
        except Exception:
            # Don't fail logging if cleanup fails
            pass

    # Enforce maximum logs per branch if configured
    max_logs = get_config_value("database", "max_logs_per_branch", 1000)
    if max_logs > 0:
        try:
            conn = sqlite3.connect(get_db_path())
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM logs WHERE branch = ? AND id NOT IN (SELECT id FROM logs WHERE branch = ? ORDER BY timestamp DESC LIMIT ?)",
                (branch, branch, max_logs),
            )
            conn.commit()
            conn.close()
        except Exception:
            # Don't fail logging if cleanup fails
            pass


def fetch_branch_logs(
    branch: str = None, limit: int = None
) -> List[Dict[str, Any]]:
    """Fetch logs for the current or specified branch, newest first.
    
    Args:
        branch: Branch name (default: current branch)
        limit: Maximum number of logs to return (default: from config)
        
    Returns:
        List of log entries with timestamp, branch, message, and extra data
        
    Note:
        If no limit is specified, uses the default_limit from configuration.
        Returns empty list if limit is <= 0.
    """
    ensure_db()
    if branch is None:
        branch = get_current_branch()

    # Use configured default limit if none provided
    if limit is None:
        limit = get_config_value("logging", "default_limit", 50)

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


def cleanup_deleted_branches() -> int:
    """Delete logs for branches that no longer exist.
    
    Returns:
        Number of deleted log entries
        
    Note:
        This function compares logged branches with existing Git branches
        and removes logs for branches that have been deleted.
    """
    ensure_db()
    from git import Repo
    repo = Repo(search_parent_directories=True)
    existing_branches = {b.name for b in repo.branches}
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT branch FROM logs")
    logged_branches = {row[0] for row in cursor.fetchall()}
    deleted_count = 0
    for branch in logged_branches:
        if branch not in existing_branches:
            cursor.execute("DELETE FROM logs WHERE branch = ?", (branch,))
            deleted_count += cursor.rowcount
    conn.commit()
    conn.close()
    return deleted_count


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


def get_current_branch() -> str:
    """Get the current Git branch or raise an error if not in a repo."""
    from git import GitCommandError, Repo
    
    try:
        repo = Repo(search_parent_directories=True)
        return repo.active_branch.name
    except GitCommandError:
        raise ValueError("Not in a Git repository. Eidex requires a Git repo.")
