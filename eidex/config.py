"""Configuration management for Eidex."""

import os
from typing import Any, Dict

# TOML parsing with fallback for different Python versions
_tomllib = None
try:
    import tomllib  # Python 3.11+
    _tomllib = tomllib
except ImportError:
    try:
        import tomli  # Python 3.6-3.10
        _tomllib = tomli
    except ImportError:
        pass

# Default configuration values
DEFAULT_CONFIG = {
    "database": {
        "filename": ".eidex-logs.db",
        "max_logs_per_branch": 1000,
        "auto_cleanup_old_logs": True,
        "cleanup_days_threshold": 90,
    },
    "logging": {
        "default_limit": 50,
        "timestamp_format": "iso",
        "include_branch_in_output": True,
    },
    "git": {
        "auto_add_to_gitignore": True,
        "gitignore_entries": [".eidex/", ".eidex-cache/"],
    },
}


def get_repo_root() -> str:
    """Get the root directory of the current Git repo."""
    from git import GitCommandError, Repo
    
    try:
        repo = Repo(search_parent_directories=True)
        return repo.working_dir
    except GitCommandError:
        raise ValueError(
            "Not in a Git repository. Eidex requires a Git repo to store logs."
        )


def get_config_path() -> str:
    """Get the path to the eidex configuration file."""
    repo_root = get_repo_root()
    return os.path.join(repo_root, "eidex.toml")


def load_config() -> Dict[str, Any]:
    """Load configuration from eidex.toml, creating default if needed."""
    config_path = get_config_path()

    # Create default config if it doesn't exist
    if not os.path.exists(config_path):
        from .file_generators import create_default_config
        create_default_config()

    # Create AI context file if it doesn't exist
    context_path = os.path.join(get_repo_root(), ".eidex", "AI_CONTEXT.md")
    if not os.path.exists(context_path):
        from .file_generators import create_ai_context_file
        create_ai_context_file()
        print(f"Created AI context file: {context_path}")
        print(
            "AI agents can now reference this file for comprehensive usage instructions."
        )

    # Parse TOML file if available
    if _tomllib is not None:
        try:
            with open(config_path, "rb") as f:
                file_config = _tomllib.load(f)

            # Merge with defaults (file config takes precedence)
            merged_config = {}
            for section, values in DEFAULT_CONFIG.items():
                merged_config[section] = DEFAULT_CONFIG[section].copy()
                if section in file_config:
                    merged_config[section].update(file_config[section])

            return merged_config
        except Exception as e:
            print(f"Warning: Could not parse {config_path}: {e}")
            print("Using default configuration.")
            return DEFAULT_CONFIG
    else:
        print("Warning: TOML parsing not available. Install tomli for Python < 3.11")
        print("Using default configuration.")
        return DEFAULT_CONFIG


def get_config_value(section: str, key: str, default: Any = None) -> Any:
    """Get a configuration value from the specified section."""
    config = load_config()
    return config.get(section, {}).get(key, default)
