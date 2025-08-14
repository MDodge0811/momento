"""Eidex: Branch-aware AI logging library.

This module provides the main public API for logging AI-assisted development work.
"""

# Import the main functions from the modular components
from eidex.config import get_config_value, load_config, get_repo_root
from eidex.database import (
    cleanup_deleted_branches,
    fetch_branch_logs,
    log_work,
    prune_old_logs,
    ensure_db,
    get_current_branch,
    get_db_path,
)
from eidex.file_generators import create_default_config, create_ai_context_file

# Public API functions
__all__ = [
    "log_work",
    "fetch_branch_logs", 
    "cleanup_deleted_branches",
    "prune_old_logs",
    "load_config",
    "get_config_value",
    "create_default_config",
    "create_ai_context_file",
    # Additional functions that tests expect
    "ensure_db",
    "get_repo_root",
    "get_current_branch",
    "get_db_path",
]


def log_work(message: str, extra_info: dict = None) -> None:
    """Log an AI action for the current branch.
    
    Args:
        message: Description of the AI action performed
        extra_info: Optional structured data about the action
    """
    from eidex.database import log_work as _log_work
    return _log_work(message, extra_info)


def fetch_branch_logs(branch: str = None, limit: int = None) -> list:
    """Fetch logs for the current or specified branch.
    
    Args:
        branch: Branch name (default: current branch)
        limit: Maximum number of logs to return (default: from config)
        
    Returns:
        List of log entries with timestamp, branch, message, and extra data
    """
    from eidex.database import fetch_branch_logs as _fetch_branch_logs
    return _fetch_branch_logs(branch, limit)


def cleanup_deleted_branches() -> int:
    """Delete logs for branches that no longer exist.
    
    Returns:
        Number of deleted log entries
    """
    from eidex.database import cleanup_deleted_branches as _cleanup_deleted_branches
    return _cleanup_deleted_branches()


def prune_old_logs(days: int) -> int:
    """Delete logs older than the specified number of days.
    
    Args:
        days: Age threshold in days
        
    Returns:
        Number of deleted log entries
    """
    from eidex.database import prune_old_logs as _prune_old_logs
    return _prune_old_logs(days)


def get_config_value(section: str, key: str, default=None) -> any:
    """Get a configuration value from the specified section.
    
    Args:
        section: Configuration section name
        key: Configuration key name
        default: Default value if not found
        
    Returns:
        Configuration value or default
    """
    from eidex.config import get_config_value as _get_config_value
    return _get_config_value(section, key, default)


def load_config() -> dict:
    """Load the current Eidex configuration.
    
    Returns:
        Dictionary containing all configuration values
    """
    from eidex.config import load_config as _load_config
    return _load_config()


def create_default_config() -> str:
    """Create or recreate the default configuration file.
    
    Returns:
        Path to the created configuration file
    """
    from eidex.file_generators import create_default_config as _create_default_config
    return _create_default_config()


def create_ai_context_file() -> str:
    """Create or recreate the AI context file.
    
    Returns:
        Path to the created AI context file
    """
    from eidex.file_generators import create_ai_context_file as _create_ai_context_file
    return _create_ai_context_file()


def ensure_db() -> str:
    """Initialize SQLite DB with table and indexes, add to .gitignore.
    
    Returns:
        Path to the database file
    """
    from eidex.database import ensure_db as _ensure_db
    return _ensure_db()


def get_repo_root() -> str:
    """Get the root directory of the current Git repo.
    
    Returns:
        Absolute path to the repository root
        
    Raises:
        ValueError: If not in a Git repository
    """
    from eidex.config import get_repo_root as _get_repo_root
    return _get_repo_root()


def get_current_branch() -> str:
    """Get the current Git branch or raise an error if not in a repo.
    
    Returns:
        Name of the current branch
        
    Raises:
        ValueError: If not in a Git repository
    """
    from eidex.database import get_current_branch as _get_current_branch
    return _get_current_branch()


def get_db_path() -> str:
    """Get the path to the repo-specific SQLite DB.
    
    Returns:
        Absolute path to the database file
    """
    from eidex.database import get_db_path as _get_db_path
    return _get_db_path()


def main():
    """Main CLI entry point."""
    from eidex.cli import main as cli_main
    return cli_main()


if __name__ == "__main__":
    main()
