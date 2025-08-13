import json
import os
import shutil
import sqlite3

# Import the functions we want to test
import sys
import tempfile
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import eidex


class TestEidex:
    """Test suite for Eidex library functions."""

    def setup_method(self):
        """Set up test environment before each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)

        # Initialize git repo for testing
        os.system("git init -q")
        os.system('git config user.name "Test User"')
        os.system('git config user.email "test@example.com"')
        os.system('git commit --allow-empty -m "Initial commit" -q')

        # Create a test branch
        os.system("git checkout -b test-branch -q")

        # Mock the database path to use temp directory
        self.patcher = patch("eidex.get_repo_root")
        self.mock_get_repo_root = self.patcher.start()
        self.mock_get_repo_root.return_value = self.temp_dir

    def teardown_method(self):
        """Clean up after each test."""
        self.patcher.stop()
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir)

    def test_get_db_path(self):
        """Test database path generation."""
        with patch("eidex.get_repo_root") as mock_repo:
            mock_repo.return_value = "/test/repo"
            db_path = eidex.get_db_path()
            assert db_path == "/test/repo/.eidex-logs.db"

    def test_ensure_db_creates_database(self):
        """Test database creation and initialization."""
        eidex.ensure_db()

        db_path = os.path.join(self.temp_dir, ".eidex-logs.db")
        assert os.path.exists(db_path)

        # Check table structure
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='logs'"
        )
        assert cursor.fetchone() is not None

        # Check columns
        cursor.execute("PRAGMA table_info(logs)")
        columns = {row[1] for row in cursor.fetchall()}
        expected_columns = {"id", "timestamp", "branch", "message", "extra"}
        assert columns == expected_columns

        # Check index
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND name='idx_branch_timestamp'"
        )
        assert cursor.fetchone() is not None

        conn.close()

    def test_ensure_db_adds_to_gitignore(self):
        """Test that database is added to .gitignore."""
        eidex.ensure_db()

        gitignore_path = os.path.join(self.temp_dir, ".gitignore")
        assert os.path.exists(gitignore_path)

        with open(gitignore_path, "r") as f:
            content = f.read()
            assert ".eidex-logs.db" in content

    def test_ensure_db_doesnt_duplicate_gitignore_entry(self):
        """Test that .gitignore entries aren't duplicated."""
        # Add entry manually first
        gitignore_path = os.path.join(self.temp_dir, ".gitignore")
        with open(gitignore_path, "w") as f:
            f.write(".eidex-logs.db\n")

        eidex.ensure_db()

        with open(gitignore_path, "r") as f:
            content = f.read()
            # Should only appear once
            assert content.count(".eidex-logs.db") == 1

    def test_get_current_branch(self):
        """Test getting current git branch."""
        branch = eidex.get_current_branch()
        assert branch == "test-branch"

    def test_get_current_branch_outside_git(self):
        """Test error when not in git repository."""
        # Mock the Git repository detection to simulate being outside a git repo
        with patch("eidex.Repo") as mock_repo_class:
            # Make the Repo constructor raise GitCommandError
            from git import GitCommandError

            mock_repo_class.side_effect = GitCommandError("Not a git repository")

            with pytest.raises(
                ValueError, match="Not in a Git repository. Eidex requires a Git repo."
            ):
                eidex.get_current_branch()

    def test_log_work(self):
        """Test logging work actions."""
        eidex.log_work("Test message")

        # Check database
        db_path = os.path.join(self.temp_dir, ".eidex-logs.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT message, branch, extra FROM logs WHERE message = 'Test message'"
        )
        row = cursor.fetchone()

        assert row is not None
        assert row[0] == "Test message"
        assert row[1] == "test-branch"
        assert row[2] is None

        conn.close()

    def test_log_work_with_extra(self):
        """Test logging work actions with extra information."""
        extra_info = {"file": "test.py", "action": "created"}
        eidex.log_work("Test message", extra_info)

        # Check database
        db_path = os.path.join(self.temp_dir, ".eidex-logs.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT message, branch, extra FROM logs WHERE message = 'Test message'"
        )
        row = cursor.fetchone()

        assert row is not None
        assert row[0] == "Test message"
        assert row[1] == "test-branch"
        assert json.loads(row[2]) == extra_info

        conn.close()

    def test_fetch_branch_logs(self):
        """Test fetching logs for current branch."""
        # Add some test logs
        eidex.log_work("Message 1")
        eidex.log_work("Message 2")

        logs = eidex.fetch_branch_logs()

        assert len(logs) == 2
        assert logs[0]["message"] == "Message 2"  # Newest first
        assert logs[1]["message"] == "Message 1"
        assert all(log["branch"] == "test-branch" for log in logs)
        assert all("timestamp" in log for log in logs)

    def test_fetch_branch_logs_with_limit(self):
        """Test fetching logs with limit."""
        # Add some test logs
        for i in range(10):
            eidex.log_work(f"Message {i}")

        logs = eidex.fetch_branch_logs(limit=5)
        assert len(logs) == 5
        assert logs[0]["message"] == "Message 9"  # Newest first

    def test_fetch_branch_logs_specific_branch(self):
        """Test fetching logs for specific branch."""
        # Switch to main branch and add logs
        os.system("git checkout main -q")
        eidex.log_work("Main branch message")

        # Switch back to test branch
        os.system("git checkout test-branch -q")
        eidex.log_work("Test branch message")

        # Fetch logs for main branch
        logs = eidex.fetch_branch_logs(branch="main")
        assert len(logs) == 1
        assert logs[0]["message"] == "Main branch message"
        assert logs[0]["branch"] == "main"

    def test_cleanup_deleted_branches(self):
        """Test cleanup of deleted branch logs."""
        # Add logs to current branch
        eidex.log_work("Test branch message")

        # Switch to main and add logs
        os.system("git checkout main -q")
        eidex.log_work("Main branch message")

        # Delete test branch
        os.system("git branch -D test-branch")

        # Cleanup
        eidex.cleanup_deleted_branches()

        # Check that test branch logs are gone
        logs = eidex.fetch_branch_logs(branch="test-branch")
        assert len(logs) == 0

        # Check that main branch logs remain
        logs = eidex.fetch_branch_logs(branch="main")
        assert len(logs) == 1
        assert logs[0]["message"] == "Main branch message"

    def test_prune_old_logs(self):
        """Test pruning of old logs."""
        # Add some logs
        eidex.log_work("Recent message")

        # Manually add old log to database
        db_path = os.path.join(self.temp_dir, ".eidex-logs.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        old_date = (datetime.now() - timedelta(days=10)).isoformat()
        cursor.execute(
            "INSERT INTO logs (timestamp, branch, message, extra) VALUES (?, ?, ?, ?)",
            (old_date, "test-branch", "Old message", None),
        )
        conn.commit()
        conn.close()

        # Prune logs older than 5 days
        deleted_count = eidex.prune_old_logs(5)
        assert deleted_count == 1

        # Check that old log is gone
        logs = eidex.fetch_branch_logs()
        assert len(logs) == 1
        assert logs[0]["message"] == "Recent message"


class TestEidexCLI:
    """Test suite for Eidex CLI functionality."""

    def setup_method(self):
        """Set up test environment before each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)

        # Initialize git repo for testing
        os.system("git init -q")
        os.system('git config user.name "Test User"')
        os.system('git config user.email "test@example.com"')
        os.system('git commit --allow-empty -m "Initial commit" -q')

        # Mock the database path
        self.patcher = patch("eidex.get_repo_root")
        self.mock_get_repo_root = self.patcher.start()
        self.mock_get_repo_root.return_value = self.temp_dir

    def teardown_method(self):
        """Clean up after each test."""
        self.patcher.stop()
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir)

    def test_cli_log_work(self):
        """Test CLI log_work command."""
        # Test basic logging using the eidex.py file directly
        eidex_script = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "eidex.py"
        )
        result = os.system(f'python3 {eidex_script} log_work "CLI test message"')
        assert result == 0

    def test_cli_log_work_with_extra(self):
        """Test CLI log_work command with extra data."""
        extra_json = '{"file": "test.py", "action": "created"}'
        eidex_script = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "eidex.py"
        )
        result = os.system(
            f"python3 {eidex_script} log_work \"CLI test message\" --extra '{extra_json}'"
        )
        assert result == 0

    def test_cli_fetch_branch_logs(self):
        """Test CLI fetch_branch_logs command."""
        # Test fetching
        eidex_script = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "eidex.py"
        )
        result = os.system(f"python3 {eidex_script} fetch_branch_logs")
        assert result == 0

    def test_cli_cleanup_deleted_branches(self):
        """Test CLI cleanup_deleted_branches command."""
        eidex_script = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "eidex.py"
        )
        result = os.system(f"python3 {eidex_script} cleanup_deleted_branches")
        assert result == 0

    def test_cli_prune_old_logs(self):
        """Test CLI prune_old_logs command."""
        eidex_script = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "eidex.py"
        )
        result = os.system(f"python3 {eidex_script} prune_old_logs 30")
        assert result == 0


class TestEidexEdgeCases:
    """Test suite for edge cases and error conditions."""

    def setup_method(self):
        """Set up test environment before each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)

        # Initialize git repo for testing
        os.system("git init -q")
        os.system('git config user.name "Test User"')
        os.system('git config user.email "test@example.com"')
        os.system('git commit --allow-empty -m "Initial commit" -q')

        # Mock the database path
        self.patcher = patch("eidex.get_repo_root")
        self.mock_get_repo_root = self.patcher.start()
        self.mock_get_repo_root.return_value = self.temp_dir

    def teardown_method(self):
        """Clean up after each test."""
        self.patcher.stop()
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir)

    def test_log_work_empty_message(self):
        """Test logging with empty message."""
        eidex.log_work("")

        logs = eidex.fetch_branch_logs()
        assert len(logs) == 1
        assert logs[0]["message"] == ""

    def test_log_work_very_long_message(self):
        """Test logging with very long message."""
        long_message = "x" * 10000
        eidex.log_work(long_message)

        logs = eidex.fetch_branch_logs()
        assert len(logs) == 1
        assert logs[0]["message"] == long_message

    def test_log_work_complex_extra_data(self):
        """Test logging with complex extra data."""
        complex_data = {
            "nested": {"deep": {"structure": [1, 2, 3]}},
            "unicode": "café 🚀",
            "special_chars": "!@#$%^&*()",
            "numbers": [1.5, -2, 0],
            "boolean": True,
            "null": None,
        }

        eidex.log_work("Complex data test", complex_data)

        logs = eidex.fetch_branch_logs()
        assert len(logs) == 1
        assert logs[0]["extra"] == complex_data

    def test_fetch_branch_logs_nonexistent_branch(self):
        """Test fetching logs for non-existent branch."""
        logs = eidex.fetch_branch_logs(branch="nonexistent")
        assert len(logs) == 0

    def test_fetch_branch_logs_negative_limit(self):
        """Test fetching logs with negative limit."""
        eidex.log_work("Test message")

        # Should handle negative limit gracefully
        logs = eidex.fetch_branch_logs(limit=-5)
        assert len(logs) == 0

    def test_fetch_branch_logs_zero_limit(self):
        """Test fetching logs with zero limit."""
        eidex.log_work("Test message")

        logs = eidex.fetch_branch_logs(limit=0)
        assert len(logs) == 0

    def test_fetch_branch_logs_very_large_limit(self):
        """Test fetching logs with very large limit."""
        eidex.log_work("Test message")

        logs = eidex.fetch_branch_logs(limit=1000000)
        assert len(logs) == 1  # Should only return what exists
