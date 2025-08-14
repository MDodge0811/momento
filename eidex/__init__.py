"""Eidex: Branch-aware AI logging library.

This module provides the main public API for logging AI-assisted development work.
"""

from .config import get_config_value, load_config, get_repo_root
from .database import (
    cleanup_deleted_branches,
    fetch_branch_logs,
    log_work,
    prune_old_logs,
    ensure_db,
    get_current_branch,
    get_db_path,
)
from .file_generators import create_default_config, create_ai_context_file

__version__ = "0.1.0"
__all__ = [
    "cleanup_deleted_branches",
    "create_ai_context_file", 
    "create_default_config",
    "fetch_branch_logs",
    "get_config_value",
    "load_config",
    "log_work",
    "prune_old_logs",
    # Additional functions that tests expect
    "ensure_db",
    "get_repo_root",
    "get_current_branch",
    "get_db_path",
]


# Direct function assignments - no lazy imports
# These maintain the original functions while providing clean public API access
log_work = log_work
fetch_branch_logs = fetch_branch_logs
cleanup_deleted_branches = cleanup_deleted_branches
prune_old_logs = prune_old_logs
get_config_value = get_config_value
load_config = load_config
create_default_config = create_default_config
create_ai_context_file = create_ai_context_file
ensure_db = ensure_db
get_repo_root = get_repo_root
get_current_branch = get_current_branch
get_db_path = get_db_path


def main():
    """Main CLI entry point."""
    from .cli import main as cli_main
    return cli_main()


if __name__ == "__main__":
    main()
