# Eidex

**Eidex** is a lightweight, branch-aware logging library for AI-assisted coding workflows. It allows developers to log actions performed by AI tools (e.g., code generation, refactoring) in a Git repository, associating logs with the current Git branch. Logs are stored in a repo-specific SQLite database (`.eidex/.eidex-logs.db`), which is automatically git-ignored to prevent committing sensitive data. The library provides a simple command-line interface (CLI) and Python API, making it easy to integrate with AI tools like Cursor.

## Features

- **Branch-Aware Logging**: Logs are tied to the current Git branch, ensuring context is preserved when switching branches.
- **Repo-Specific Storage**: Each Git repository has its own `.eidex/.eidex-logs.db`, preventing cross-repo interference.
- **Simple CLI**: Run commands like `eidex log_work "AI refactored code"` from any Git repo.
- **Python API**: Programmatically log and retrieve actions with `eidex.log_work()` and `eidex.fetch_branch_logs()`.
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
   git clone https://github.com/yourname/eidex.git
   cd eidex
   ```
2. Install globally:
   ```bash
   pip install .
   ```
   This installs `eidex` and creates an `eidex` command in `~/.local/bin` or `/usr/local/bin`.

3. Ensure the install directory is in your `PATH`:
   ```bash
   echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
   source ~/.zshrc
   ```

4. Verify:
   ```bash
   eidex --help
   ```

Alternatively, install directly from PyPI (once published):
```bash
pip install eidex
```

## Usage

Momento provides both a CLI and a Python API for logging and retrieving AI actions in a Git repository. Logs are stored in `.eidex/.eidex-logs.db` in the repo’s root, automatically added to `.gitignore`.

### Command-Line Interface (CLI)
Run `eidex` commands from any Git repository:

```bash
# Log an AI action
eidex log_work "AI refactored user auth module" --extra '{"file": "auth.php"}'

# Fetch logs for the current branch (latest 50)
eidex fetch_branch_logs

# Fetch logs for a specific branch
eidex fetch_branch_logs --branch feature-x --limit 10

# Delete logs for branches that no longer exist
eidex cleanup_deleted_branches

# Delete logs older than 90 days
eidex prune_old_logs 90

# Delete oldest logs if database exceeds 5MB
eidex prune_by_size 5.0
```

### Python API
Use Eidex programmatically in Python scripts or AI tool integrations:

```python
import eidex

# Log an action
eidex.log_work("AI generated user model", {"file": "user.php"})

# Fetch logs (current branch, latest 50)
logs = eidex.fetch_branch_logs()
print(logs)  # List of dicts: [{'timestamp': '...', 'message': '...', 'extra': {...}}, ...]

# Fetch specific branch
logs = eidex.fetch_branch_logs(branch="feature-x", limit=10)

# Maintenance
eidex.cleanup_deleted_branches()
print(f"Deleted {eidex.prune_old_logs(90)} old logs")
print(f"Deleted {eidex.prune_by_size(5.0)} logs to reduce size")
```

### AI Tool Integration
Integrate with AI tools like Cursor that support CLI or Python execution:

#### Direct CLI Calls
```bash
# In AI prompts
After each action, run: `eidex log_work "AI made change X"`
To load context: `eidex fetch_branch_logs`
```

#### In a PHP Project
If your codebase is PHP, use `exec` or `shell_exec`:
```php
<?php
exec('eidex log_work "AI updated auth module" --extra \'{"file":"auth.php"}\'');
$logs = json_decode(shell_exec('eidex fetch_branch_logs'), true);
print_r($logs);
```

#### In a Python Script
```python
import eidex
eidex.log_work("AI action", {"context": "some metadata"})
logs = eidex.fetch_branch_logs()
```

## How It Works
- **Storage**: Logs are stored in a SQLite database (`.eidex/.eidex-logs.db`) in the .eidex/ directory, ensuring isolation between repos.
- **Branch Detection**: Uses `gitpython` to detect the current branch. If not in a Git repo, commands fail with an error.
- **Automatic Setup**: The database and `.gitignore` entry are created on first use.
- **Log Structure**: Each log entry includes:
  - `timestamp`: ISO 8601 datetime (e.g., `2025-08-12T11:18:56`).
  - `branch`: The Git branch name.
  - `message`: The AI action description.
  - `extra`: Optional JSON metadata (e.g., `{"file": "auth.php"}`).

## Maintenance
- **Cleanup**: `eidex cleanup_deleted_branches` removes logs for branches no longer in the repo.
- **Pruning**:
  - `eidex prune_old_logs 90`: Deletes logs older than 90 days.
  - `eidex prune_by_size 5.0`: Deletes oldest logs if the database exceeds 5MB, with automatic `VACUUM` to shrink the file.
- **Sharing**: Manually copy `.eidex/.eidex-logs.db` to another repo for sharing logs.

## Testing
Test in a Git repository:
```bash
cd my-repo
git checkout -b test-branch
eidex log_work "Test AI action"
eidex fetch_branch_logs  # Shows the log
git checkout main
git branch -d test-branch
eidex cleanup_deleted_branches  # Removes test-branch logs
```

If run outside a Git repo:
```bash
cd ~/non-repo-dir
eidex log_work "Test"  # Fails: "Error: Not in a Git repository."
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