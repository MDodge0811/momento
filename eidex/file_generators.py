"""File generation utilities for Eidex."""

import os
from .config import get_repo_root, get_config_path


def ensure_eidex_directory() -> str:
    """Ensure the .eidex directory exists."""
    eidex_dir = os.path.join(get_repo_root(), ".eidex")
    if not os.path.exists(eidex_dir):
        os.makedirs(eidex_dir)
    return eidex_dir


def create_default_config() -> str:
    """Create a default eidex.toml configuration file."""
    config_path = get_config_path()

    config_content = """# Eidex Configuration File
# This file contains customizable settings for the Eidex logging system

[database]
# Database file name (relative to .eidex directory)
filename = ".eidex-logs.db"
# Maximum number of logs to keep per branch
max_logs_per_branch = 1000
# Automatically clean up old logs
auto_cleanup_old_logs = true
# Days threshold for automatic cleanup
cleanup_days_threshold = 90

[logging]
# Default number of logs to fetch
default_limit = 50
# Timestamp format: "iso" or "human"
timestamp_format = "iso"
# Include branch name in output
include_branch_in_output = true

[git]
# Automatically add database to .gitignore
auto_add_to_gitignore = true
# Additional entries to add to .gitignore
gitignore_entries = [".eidex.toml", ".eidex/"]
"""

    with open(config_path, "w") as f:
        f.write(config_content)

    if os.path.exists(config_path):
        print(f"Updated configuration file: {config_path}")
    else:
        print(f"Created default configuration file: {config_path}")
    print("You can customize these settings by editing eidex.toml")
    
    return config_path


def create_ai_context_file() -> str:
    """Create a comprehensive AI context file for Eidex usage."""
    # Ensure .eidex directory exists
    ensure_eidex_directory()

    context_path = os.path.join(get_repo_root(), ".eidex", "AI_CONTEXT.md")

    context_content = """# Eidex AI Agent Context

**Version**: 1.0 (Updated August 13, 2025)

## Overview

Eidex is a lightweight, branch-aware logging library for AI-assisted coding workflows. It integrates with Git to associate logs with the current branch and stores them in a SQLite database (`.eidex/.eidex-logs.db`). Eidex supports both CLI and Python API interfaces, with configuration via `eidex.toml`.

## Command Summary

| Command                     | Purpose                              | Example Usage                              |
|-----------------------------|--------------------------------------|--------------------------------------------|
| `log_work`                  | Log an AI action                     | `eidex log_work "Refactored module"`       |
| `fetch_branch_logs`         | Retrieve logs for a branch           | `eidex fetch_branch_logs --limit 10`       |
| `prune_old_logs`            | Remove logs older than X days        | `eidex prune_old_logs 30`                  |
| `cleanup_deleted_branches`  | Remove logs for deleted branches     | `eidex cleanup_deleted_branches`           |
| `show_config`               | Display current configuration        | `eidex show_config`                        |
| `init_config`               | Recreate configuration file          | `eidex init_config`                        |

## Instructions for AI Agents

- Parse this file to execute Eidex commands for logging and managing AI-assisted development tasks.
- Always include structured `extra_info` with consistent keys (e.g., `type`, `component`, `severity`) when logging.
- Validate the presence and settings of `eidex.toml` before executing commands.
- Prioritize recent logs using `fetch_branch_logs` for context-aware responses.
- Handle errors as specified in the `Error Handling` section.

## Features

- **Branch-Aware Logging**: Associates logs with the current Git branch.
- **SQLite Storage**: Stores logs in `.eidex/.eidex-logs.db`.
- **Git Integration**: Automatically adds `.eidex/` to `.gitignore`.
- **CLI & Python API**: Supports command-line and programmatic interfaces.
- **Customizable Configuration**: Configured via `eidex.toml`.
- **Organized Structure**: Stores generated files in `.eidex/` directory.

## Usage

### Logging Actions

**Command**: `eidex.log_work(message, extra_info=None)`

- **Input**:
  - `message`: String describing the AI action performed (required).
  - `extra_info`: Dictionary with optional structured data about the action.
- **Output**: None (logs are stored in `.eidex/.eidex-logs.db`).
- **Example**:

  ```bash
  eidex log_work "Refactored user authentication module" --extra_info '{"type": "refactoring", "component": "auth"}'
  ```

  ```python
  import eidex
  eidex.log_work("Refactored user authentication module", extra_info={
      "type": "refactoring",
      "component": "auth"
  })
  ```

### Retrieving Logs

**Command**: `eidex.fetch_branch_logs(branch=None, limit=None)`

- **Input**:
  - `branch`: String specifying the branch name (optional, defaults to current branch).
  - `limit`: Integer specifying the maximum number of logs to return (optional, defaults to `default_limit` in `eidex.toml`).
- **Output**: List of log entries with timestamp, branch, message, and extra data.
- **Example**:

  ```bash
  eidex fetch_branch_logs --limit 10
  eidex fetch_branch_logs --branch feature/user-auth
  ```

  ```python
  logs = eidex.fetch_branch_logs(limit=10)
  logs = eidex.fetch_branch_logs(branch="feature/user-auth")
  ```

### Managing Configuration

**Commands**:

- `eidex.show_config()`: Display current configuration.
  - **Output**: Dictionary containing all configuration values.
- `eidex.create_default_config()`: Create or recreate the default configuration file.
  - **Output**: Path to the created `eidex.toml` file.
- `eidex.prune_old_logs(days)`: Delete logs older than the specified number of days.
  - **Input**: `days`: Integer (age threshold in days).
  - **Output**: Number of deleted log entries.
- `eidex.cleanup_deleted_branches()`: Delete logs for branches that no longer exist.
  - **Output**: Number of deleted log entries.
- **Example**:

  ```bash
  eidex show_config
  eidex prune_old_logs 30
  ```

  ```python
  config = eidex.load_config()
  deleted = eidex.prune_old_logs(30)
  ```

### Database and Repository Management

**Commands**:

- `eidex.ensure_db()`: Initialize SQLite database with table and indexes, add to `.gitignore`.
  - **Output**: Path to the database file (`.eidex/.eidex-logs.db`).
- `eidex.get_repo_root()`: Get the root directory of the current Git repository.
  - **Output**: Absolute path to the repository root.
  - **Raises**: `ValueError` if not in a Git repository.
- `eidex.get_current_branch()`: Get the current Git branch.
  - **Output**: Name of the current branch.
  - **Raises**: `ValueError` if not in a Git repository.
- `eidex.get_db_path()`: Get the path to the SQLite database.
  - **Output**: Absolute path to the database file.

- **Example**:

  ```python
  db_path = eidex.ensure_db()
  repo_root = eidex.get_repo_root()
  branch = eidex.get_current_branch()
  ```

## Configuration

The `eidex.toml` file defines settings. AI agents must validate its presence and parse it before executing commands.

```toml
[database]
filename = ".eidex-logs.db"           # Database file
max_logs_per_branch = 1000           # Maximum logs per branch
auto_cleanup_old_logs = true         # Enable automatic cleanup
cleanup_days_threshold = 90          # Days before logs are pruned

[logging]
default_limit = 50                    # Default number of logs to fetch
timestamp_format = "iso"             # ISO 8601 timestamp format
include_branch_in_output = true      # Include branch name in log output

[git]
auto_add_to_gitignore = true         # Auto-add .eidex/ to .gitignore
gitignore_entries = [".eidex-logs.db"] # Files to ignore
```

## Directory Structure

- `eidex.toml`: Configuration file (top-level).
- `.eidex/`:
  - `.eidex-logs.db`: SQLite database for logs.
  - `AI_CONTEXT.md`: This context file for AI agents.
  - `.eidex-cache/`: Optional cache directory.
- `.gitignore`: Automatically updated to include `.eidex/`.

## AI Agent Use Cases

### Code Generation

```python
eidex.log_work("Generated REST API", extra_info={
    "type": "code_generation",
    "framework": "FastAPI",
    "endpoints": ["/users", "/orders"]
})
```

### Bug Fixing

```python
eidex.log_work("Fixed null pointer in payment module", extra_info={
    "type": "bug_fix",
    "severity": "high",
    "root_cause": "uninitialized variable"
})
```

### Refactoring

```python
eidex.log_work("Refactored database queries", extra_info={
    "type": "refactoring",
    "reason": "performance_optimization",
    "affected_files": ["models/", "controllers/"]
})
```

## Guidelines

- **Do**:
  - Use descriptive messages (e.g., "Refactored login to use JWT" instead of "Refactored code").
  - Include structured `extra_info` with consistent keys (e.g., `type`, `component`, `severity`).
  - Run `prune_old_logs` periodically to manage storage.
- **Don't**:
  - Log vague messages without `extra_info` (e.g., `eidex.log_work("Fixed bug")`).
  - Use inconsistent `extra_info` keys across logs.
  - Ignore `eidex.toml` settings (e.g., `default_limit`).

## Error Handling

- **Not in a Git repository**:
  - **Check**: Run `eidex.get_repo_root()` or `eidex.get_current_branch()`.
  - **Action**: If `ValueError` is raised, suggest `git init` or changing to a valid repository.
- **Missing `eidex.toml`**:
  - **Action**: Run `eidex.create_default_config()` to recreate the configuration.
- **Database locked**:
  - **Action**: Retry after a 1-second delay, up to 3 attempts.
- **Logs not showing expected limit**:
  - **Check**: Run `eidex.show_config()` to verify `default_limit` in `eidex.toml`.

## Log Structure Schema

```json
{
  "timestamp": "string (ISO 8601 format, e.g., '2025-08-13T21:41:00Z')",
  "branch": "string (e.g., 'feature/user-auth')",
  "message": "string (e.g., 'Refactored user authentication')",
  "extra_info": {
    "type": "string (e.g., 'bug_fix', 'code_generation')",
    "additional_properties": "any (e.g., 'component', 'severity')"
  }
}
```

## Analyzing Logs

### Recent Activity

```python
logs = eidex.fetch_branch_logs(limit=20)
for log in logs:
    print(f"{log['timestamp']}: {log['message']}")
    if log['extra_info']:
        print(f"  Extra Info: {log['extra_info']}")
```

### Work Type Analysis

```python
def analyze_log_types(limit=500):
    logs = eidex.fetch_branch_logs(limit=limit)
    types = {}
    for log in logs:
        log_type = log.get('extra_info', {}).get('type', 'unknown')
        types[log_type] = types.get(log_type, 0) + 1
    return types
```

## Extending Eidex

- **Custom Log Types**: Add new `type` values in `extra_info` (e.g., `type: "experiment"`).
- **Tool Integration**: Use the Python API to integrate with external tools.
- **Example**:

  ```python
  eidex.log_work("Ran ML experiment", extra_info={
      "type": "experiment",
      "model": "GPT-4",
      "dataset": "imagenet"
  })
  ```

## Troubleshooting

- Run `eidex --help` for command overview.
- Use `eidex.show_config()` to verify settings.
- Check `eidex.toml` for configuration issues.
- Context file location: `.eidex/AI_CONTEXT.md`.

---

**Note**: Eidex is designed to be simple and unobtrusive. Use it to track AI-assisted development work and maintain a clear history of repository activities.

| Command | Description | Example |
|---------|-------------|---------|
| `log_work` | Log an action | `eidex log_work "message"` |
| `fetch_branch_logs` | Get logs | `eidex fetch_branch_logs --limit 10` |
| `cleanup_deleted_branches` | Clean up | `eidex cleanup_deleted_branches` |
| `prune_old_logs` | Remove old | `eidex prune_old_logs 30` |
| `show_config` | Show config | `eidex show_config` |
| `init_config` | Reset config | `eidex init_config` |

---

**Remember**: Eidex is designed to be simple and unobtrusive. Use it to track your AI-assisted development work, and let it help you maintain a clear history of what's been accomplished in your repository.
"""

    with open(context_path, "w") as f:
        f.write(context_content)

    return context_path
