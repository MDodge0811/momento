# Momento

**Momento** is a lightweight, branch-aware logging library for AI-assisted coding workflows. It allows developers to log actions performed by AI tools (e.g., code generation, refactoring) in a Git repository, associating logs with the current Git branch. Logs are stored in a repo-specific SQLite database (`.momento-logs.db`), which is automatically git-ignored to prevent committing sensitive data. The library provides a simple command-line interface (CLI) and Python API, making it easy to integrate with AI tools like Cursor.

## Features

- **Branch-Aware Logging**: Logs are tied to the current Git branch, ensuring context is preserved when switching branches.
- **Repo-Specific Storage**: Each Git repository has its own `.momento-logs.db`, preventing cross-repo interference.
- **Simple CLI**: Run commands like `momento log_work "AI refactored code"` from any Git repo.
- **Python API**: Programmatically log and retrieve actions with `momento.log_work()` and `momento.fetch_branch_logs()`.
- **Automatic Cleanup**: Delete logs for branches that no longer exist.
- **Pruning**: Remove old logs (e.g., >90 days) or reduce database size (e.g., <5MB).
- **Plug-and-Play**: No setup required; the database and `.gitignore` entry are created automatically.
- **AI Integration**: Easily called by AI tools via CLI or Python, with JSON output for logs.
- **Lightweight**: Minimal dependencies (only `gitpython` for branch detection; SQLite is built-in).

## Installation

### Prerequisites
- Python 3.6+ (SQLite is included in Python's standard library).
- Git installed (`brew install git` on macOS).
- `gitpython` (installed automatically during setup).

### Install via pip
1. Clone or download the repository:
   ```bash
   git clone https://github.com/yourname/momento.git
   cd momento
   ```
2. Install globally:
   ```bash
   pip install .
   ```
   This installs `momento` and creates a `momento` command in `~/.local/bin` or `/usr/local/bin`.

3. Ensure the install directory is in your `PATH`:
   ```bash
   echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
   source ~/.zshrc
   ```

4. Verify:
   ```bash
   momento --help
   ```

Alternatively, install directly from PyPI (once published):
```bash
pip install momento
```

## Usage

Momento provides both a CLI and a Python API for logging and retrieving AI actions in a Git repository. Logs are stored in `.momento-logs.db` in the repo’s root, automatically added to `.gitignore`.

### Command-Line Interface (CLI)
Run `momento` commands from any Git repository:

```bash
# Log an AI action
momento log_work "AI refactored user auth module" --extra '{"file": "auth.php"}'

# Fetch logs for the current branch (latest 50)
momento fetch_branch_logs

# Fetch logs for a specific branch
momento fetch_branch_logs --branch feature-x --limit 10

# Delete logs for branches that no longer exist
momento cleanup_deleted_branches

# Delete logs older than 90 days
momento prune_old_logs 90

# Delete oldest logs if database exceeds 5MB
momento prune_by_size 5.0
```

### Python API
Use Momento programmatically in Python scripts or AI tool integrations:

```python
import momento

# Log an action
momento.log_work("AI generated user model", {"file": "user.php"})

# Fetch logs (current branch, latest 50)
logs = momento.fetch_branch_logs()
print(logs)  # List of dicts: [{'timestamp': '...', 'message': '...', 'extra': {...}}, ...]

# Fetch specific branch
logs = momento.fetch_branch_logs(branch="feature-x", limit=10)

# Maintenance
momento.cleanup_deleted_branches()
print(f"Deleted {momento.prune_old_logs(90)} old logs")
print(f"Deleted {momento.prune_by_size(5.0)} logs to reduce size")
```

### AI Tool Integration
Integrate with AI tools like Cursor that support CLI or Python execution:

#### Direct CLI Calls
```bash
# In AI prompts
After each action, run: `momento log_work "AI made change X"`
To load context: `momento fetch_branch_logs`
```

#### In a PHP Project
If your codebase is PHP, use `exec` or `shell_exec`:
```php
<?php
exec('momento log_work "AI updated auth module" --extra \'{"file":"auth.php"}\'');
$logs = json_decode(shell_exec('momento fetch_branch_logs'), true);
print_r($logs);
```

#### In a Python Script
```python
import momento
momento.log_work("AI action", {"context": "some metadata"})
logs = momento.fetch_branch_logs()
```

## How It Works
- **Storage**: Logs are stored in a SQLite database (`.momento-logs.db`) in the root of the current Git repository, ensuring isolation between repos.
- **Branch Detection**: Uses `gitpython` to detect the current branch. If not in a Git repo, commands fail with an error.
- **Automatic Setup**: The database and `.gitignore` entry are created on first use.
- **Log Structure**: Each log entry includes:
  - `timestamp`: ISO 8601 datetime (e.g., `2025-08-12T11:18:56`).
  - `branch`: The Git branch name.
  - `message`: The AI action description.
  - `extra`: Optional JSON metadata (e.g., `{"file": "auth.php"}`).

## Maintenance
- **Cleanup**: `momento cleanup_deleted_branches` removes logs for branches no longer in the repo.
- **Pruning**:
  - `momento prune_old_logs 90`: Deletes logs older than 90 days.
  - `momento prune_by_size 5.0`: Deletes oldest logs if the database exceeds 5MB, with automatic `VACUUM` to shrink the file.
- **Sharing**: Manually copy `.momento-logs.db` to another repo for sharing logs.

## Testing
Test in a Git repository:
```bash
cd my-repo
git checkout -b test-branch
momento log_work "Test AI action"
momento fetch_branch_logs  # Shows the log
git checkout main
git branch -d test-branch
momento cleanup_deleted_branches  # Removes test-branch logs
```

If run outside a Git repo:
```bash
cd ~/non-repo-dir
momento log_work "Test"  # Fails: "Error: Not in a Git repository."
```

## Contributing
Contributions are welcome! To contribute:
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature-x`).
3. Commit changes (`git commit -m "Add feature X"`).
4. Push to the branch (`git push origin feature-x`).
5. Open a pull request.

Please include tests and update this README if needed.

## License
MIT License. See [LICENSE](LICENSE) for details.

## Contact
For issues or feature requests, open a GitHub issue or contact [your.email@example.com](mailto:your.email@example.com).