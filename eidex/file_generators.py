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

    context_content = """# Eidex AI Agent Context Guide

## 🎯 What is Eidex?

**Eidex** is a lightweight, branch-aware logging library for AI-assisted coding workflows. It allows developers to log actions performed by AI tools (e.g., code generation, refactoring) in a Git repository, associating logs with the current Git branch.

## 🚀 Key Features

- **Branch-Aware Logging**: Automatically associates logs with current Git branch
- **SQLite Storage**: Lightweight, repo-specific database (`.eidex/.eidex-logs.db`)
- **Git Integration**: Automatically adds `.eidex/` directory to `.gitignore`
- **CLI & Python API**: Both command-line and programmatic interfaces
- **Configuration**: Customizable via `eidex.toml` file
- **Organized Structure**: All generated files stored in `.eidex/` directory

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

## 📁 Directory Structure

Eidex organizes generated files for a clean repository structure:

```
repository/
├── eidex.toml              # Configuration file (top-level)
├── .eidex/                 # Generated files directory
│   ├── .eidex-logs.db      # SQLite database
│   ├── AI_CONTEXT.md       # AI agent context file
│   └── .eidex-cache/       # Cache directory (if used)
└── .gitignore              # Git ignore file
```

The `.eidex/` directory is automatically added to `.gitignore` to prevent committing generated files.

## 🔧 Configuration

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
- AI context file is located at `.eidex/AI_CONTEXT.md`

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
"""

    with open(context_path, "w") as f:
        f.write(context_content)

    return context_path
