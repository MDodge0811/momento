import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime, timedelta
from pathlib import Path

from git import GitCommandError, Repo

# TOML parsing with fallback for different Python versions
try:
    import tomllib  # Python 3.11+
except ImportError:
    try:
        import tomli as tomllib  # Python 3.6-3.10
    except ImportError:
        tomllib = None


# Default configuration values
DEFAULT_CONFIG = {
    "database": {
        "filename": ".eidex-logs.db",
        "max_logs_per_branch": 1000,
        "auto_cleanup_old_logs": True,
        "cleanup_days_threshold": 90
    },
    "logging": {
        "default_limit": 50,
        "timestamp_format": "iso",
        "include_branch_in_output": True
    },
    "git": {
        "auto_add_to_gitignore": True,
        "gitignore_entries": [".eidex-logs.db", ".eidex-cache/"]
    }
}


def get_config_path():
    """Get the path to the eidex configuration file."""
    repo_root = get_repo_root()
    return os.path.join(repo_root, "eidex.toml")


def create_default_config():
    """Create a default eidex.toml configuration file."""
    config_path = get_config_path()
    
    config_content = '''# Eidex Configuration File
# This file contains customizable settings for the Eidex logging system

[database]
# Database file name (relative to repo root)
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
gitignore_entries = [".eidex.toml", ".eidex-logs.db", ".eidex-cache/", "EIDEX_AI_CONTEXT.md"]
'''
    
    with open(config_path, "w") as f:
        f.write(config_content)
    
    if os.path.exists(config_path):
        print(f"Updated configuration file: {config_path}")
    else:
        print(f"Created default configuration file: {config_path}")
    print("You can customize these settings by editing eidex.toml")


    """Create a comprehensive AI context file for Eidex usage."""
    context_path = os.path.join(get_repo_root(), "EIDEX_AI_CONTEXT.md")
    
    context_content = '''# Eidex AI Agent Context Guide

## 🎯 What is Eidex?

**Eidex** is a lightweight, branch-aware logging library for AI-assisted coding workflows. It allows developers to log actions performed by AI tools (e.g., code generation, refactoring) in a Git repository, associating logs with the current Git branch.

## 🚀 Key Features

- **Branch-Aware Logging**: Automatically associates logs with current Git branch
- **SQLite Storage**: Lightweight, repo-specific database (`.eidex-logs.db`)
- **Git Integration**: Automatically adds database to `.gitignore`
- **CLI & Python API**: Both command-line and programmatic interfaces
- **Configuration**: Customizable via `eidex.toml` file

## 📚 How to Use Eidex

### 1. Basic Logging

Log an AI action for the current branch:

```bash
# Command line
eidex log_work "Refactored user authentication module"

# Python API
import eidex
eidex.log_work("Refactored user authentication module")
```

### 2. Logging with Additional Context

Include structured data with your logs:

```bash
# Command line
eidex log_work "Added new API endpoint" --extra '{"endpoint": "/api/users", "method": "POST", "complexity": "medium"}'

# Python API
eidex.log_work("Added new API endpoint", {
    "endpoint": "/api/users",
    "method": "POST", 
    "complexity": "medium"
})
```

### 3. Retrieving Logs

Fetch logs for analysis or review:

```bash
# Get recent logs (uses configured default limit)
eidex fetch_branch_logs

# Get specific number of logs
eidex fetch_branch_logs --limit 10

# Get logs for specific branch
eidex fetch_branch_logs --branch feature/user-auth

# Python API
logs = eidex.fetch_branch_logs(limit=10)
logs = eidex.fetch_branch_logs(branch="feature/user-auth")
```

### 4. Maintenance Commands

Keep your logs organized:

```bash
# Clean up deleted branches
eidex cleanup_deleted_branches

# Remove old logs
eidex prune_old_logs 30  # Remove logs older than 30 days

# Show current configuration
eidex show_config

# Recreate configuration file
eidex init_config
```

## 🔧 Configuration

Eidex automatically creates an `eidex.toml` configuration file on first run. Key settings:

```toml
[database]
filename = ".eidex-logs.db"           # Database filename
max_logs_per_branch = 1000           # Max logs per branch
auto_cleanup_old_logs = true         # Auto-cleanup old logs
cleanup_days_threshold = 90          # Days threshold for cleanup

[logging]
default_limit = 50                    # Default logs to fetch
timestamp_format = "iso"             # Timestamp format
include_branch_in_output = true      # Include branch in output

[git]
auto_add_to_gitignore = true         # Auto-add to .gitignore
gitignore_entries = [".eidex-logs.db"] # Files to ignore
```

## 💡 Use Cases for AI Agents

### 1. Code Generation Tracking
```python
import eidex

# Log when generating new code
eidex.log_work("Generated user authentication middleware", {
    "type": "code_generation",
    "component": "middleware",
    "framework": "Express.js",
    "complexity": "high"
})
```

### 2. Refactoring Documentation
```python
# Log refactoring decisions
eidex.log_work("Refactored database queries for performance", {
    "type": "refactoring",
    "reason": "performance_optimization",
    "affected_files": ["models/", "controllers/"],
    "estimated_impact": "high"
})
```

### 3. Bug Fix Tracking
```python
# Log bug fixes and their context
eidex.log_work("Fixed memory leak in image processing", {
    "type": "bug_fix",
    "severity": "critical",
    "root_cause": "unclosed_file_handles",
    "testing_required": True
})
```

### 4. Feature Development
```python
# Track feature development progress
eidex.log_work("Implemented OAuth2 authentication flow", {
    "type": "feature_development",
    "status": "completed",
    "dependencies": ["passport-oauth2", "express-session"],
    "testing_coverage": "85%"
})
```

## 🔍 Analyzing Logs

### Get Recent Activity
```python
# See what's been worked on recently
recent_logs = eidex.fetch_branch_logs(limit=20)
for log in recent_logs:
    print(f"{log['timestamp']}: {log['message']}")
    if log['extra']:
        print(f"  Context: {log['extra']}")
```

### Branch-Specific Analysis
```python
# Analyze work on specific branches
feature_logs = eidex.fetch_branch_logs(branch="feature/user-auth")
bugfix_logs = eidex.fetch_branch_logs(branch="hotfix/security-patch")
```

### Structured Data Analysis
```python
# Analyze logs by type or category
logs = eidex.fetch_branch_logs(limit=100)
refactoring_logs = [log for log in logs if log.get('extra', {}).get('type') == 'refactoring']
bug_fixes = [log for log in logs if log.get('extra', {}).get('type') == 'bug_fix']
```

## 🎨 Best Practices

### 1. Descriptive Messages
```python
# Good
eidex.log_work("Refactored user authentication to use JWT tokens")

# Better
eidex.log_work("Refactored user authentication: replaced session-based auth with JWT tokens for better scalability")
```

### 2. Structured Extra Data
```python
# Use consistent keys for better analysis
eidex.log_work("Added user profile endpoint", {
    "type": "feature_development",
    "component": "api",
    "endpoint": "/api/users/profile",
    "method": "GET",
    "authentication": "required"
})
```

### 3. Regular Cleanup
```python
# Set up automatic cleanup in your workflow
# The configuration handles this automatically
```

## 🚨 Common Pitfalls

### 1. Not Using Extra Data
```python
# Don't just log the message
eidex.log_work("Fixed bug")

# Do include context
eidex.log_work("Fixed bug", {
    "type": "bug_fix",
    "component": "user_service",
    "symptom": "users couldn't log in",
    "root_cause": "expired token validation"
})
```

### 2. Inconsistent Logging
```python
# Don't mix different formats
eidex.log_work("Added feature")
eidex.log_work("Added feature", {"type": "feature"})

# Do use consistent structure
eidex.log_work("Added feature", {"type": "feature_development"})
```

## 🔗 Integration Examples

### With CI/CD Pipelines
```yaml
# .github/workflows/eidex-cleanup.yml
name: Eidex Maintenance
on:
  schedule:
    - cron: '0 2 * * 0'  # Weekly cleanup

jobs:
  cleanup:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Cleanup old logs
        run: eidex prune_old_logs 90
```

### With Development Workflows
```bash
# Pre-commit hook
#!/bin/bash
# Log the current work before committing
eidex log_work "Pre-commit: $(git diff --name-only --cached | head -5 | tr '\n' ' ')"
```

## 📊 Monitoring and Analytics

### Log Volume Tracking
```python
# Monitor how much logging is happening
logs = eidex.fetch_branch_logs(limit=1000)
daily_counts = {}
for log in logs:
    date = log['timestamp'][:10]  # Extract date
    daily_counts[date] = daily_counts.get(date, 0) + 1

print("Logs per day:", daily_counts)
```

### Work Type Analysis
```python
# Analyze what types of work are being done
logs = eidex.fetch_branch_logs(limit=500)
work_types = {}
for log in logs:
    work_type = log.get('extra', {}).get('type', 'unknown')
    work_types[work_type] = work_types.get(work_type, 0) + 1

print("Work distribution:", work_types)
```

## 🆘 Troubleshooting

### Common Issues

1. **"Not in a Git repository"**
   - Ensure you're in a Git repository
   - Run `git init` if needed

2. **Configuration not working**
   - Check `eidex.toml` exists
   - Run `eidex init_config` to recreate

3. **Logs not showing expected limit**
   - Check configuration with `eidex show_config`
   - Verify `default_limit` setting

### Getting Help

- Run `eidex --help` for command overview
- Use `eidex show_config` to check settings
- Check the `eidex.toml` file for configuration

## 🎯 Quick Reference

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
'''
    
    with open(context_path, "w") as f:
        f.write(context_content)
    
    return context_path


def load_config():
    """Load configuration from eidex.toml, creating default if needed."""
    config_path = get_config_path()
    
    # Create default config if it doesn't exist
    if not os.path.exists(config_path):
        create_default_config()
    
    # Create AI context file if it doesn't exist
    context_path = os.path.join(get_repo_root(), "EIDEX_AI_CONTEXT.md")
    if not os.path.exists(context_path):
        create_ai_context_file()
        print(f"Created AI context file: {context_path}")
        print("AI agents can now reference this file for comprehensive usage instructions.")
    
    # Parse TOML file if available
    if tomllib is not None:
        try:
            with open(config_path, "rb") as f:
                file_config = tomllib.load(f)
            
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


def get_config_value(section: str, key: str, default=None):
    """Get a configuration value from the specified section."""
    config = load_config()
    return config.get(section, {}).get(key, default)


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
    db_filename = get_config_value("database", "filename", ".eidex-logs.db")
    return os.path.join(repo_root, db_filename)


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

    # Add to .gitignore if configured to do so
    if get_config_value("git", "auto_add_to_gitignore", True):
        gitignore_path = os.path.join(get_repo_root(), ".gitignore")
        gitignore_entries = get_config_value("git", "gitignore_entries", [".eidex-logs.db"])
        
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


def get_current_branch():
    """Get the current Git branch or raise an error if not in a repo."""
    try:
        repo = Repo(search_parent_directories=True)
        return repo.active_branch.name
    except GitCommandError:
        raise ValueError("Not in a Git repository. Eidex requires a Git repo.")


def log_work(message: str, extra_info: dict | None = None):
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
                (branch, branch, max_logs)
            )
            conn.commit()
            conn.close()
        except Exception:
            # Don't fail logging if cleanup fails
            pass


def fetch_branch_logs(branch: str | None = None, limit: int = None) -> list[dict]:
    """Fetch logs for the current or specified branch, newest first."""
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
    subparsers.add_parser(
        "show_config", help="Show current configuration"
    )

    # init_config command
    subparsers.add_parser(
        "init_config", help="Create or recreate configuration file"
    )

    # create_context command
    subparsers.add_parser(
        "create_context", help="Create or recreate AI context file"
    )

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
            print("AI agents can now reference this file for comprehensive usage instructions.")

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
