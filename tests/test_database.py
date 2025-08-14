"""Tests for eidex.database module."""

import os
import tempfile
import shutil
from unittest.mock import patch

import eidex


class TestEidexDatabase:
    """Test suite for database operations."""

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

    def test_get_db_path(self):
        """Test database path generation."""
        with patch("eidex.database.get_repo_root") as mock_repo, \
             patch("eidex.database.get_config_value") as mock_config:
            mock_repo.return_value = "/test/repo"
            mock_config.return_value = ".eidex-logs.db"
            
            db_path = eidex.get_db_path()
            assert db_path == "/test/repo/.eidex/.eidex-logs.db"

    def test_ensure_db_creates_database(self):
        """Test that ensure_db creates the database file."""
        eidex.ensure_db()
        
        db_path = os.path.join(self.temp_dir, ".eidex", ".eidex-logs.db")
        assert os.path.exists(db_path)

    def test_ensure_db_adds_to_gitignore(self):
        """Test that ensure_db adds .eidex/ to .gitignore."""
        eidex.ensure_db()
        
        gitignore_path = os.path.join(self.temp_dir, ".gitignore")
        with open(gitignore_path, "r") as f:
            content = f.read()
            assert ".eidex/" in content

    def test_ensure_db_doesnt_duplicate_gitignore_entry(self):
        """Test that ensure_db doesn't duplicate .gitignore entries."""
        # Add .eidex/ to .gitignore manually first
        gitignore_path = os.path.join(self.temp_dir, ".gitignore")
        with open(gitignore_path, "w") as f:
            f.write(".eidex/\n")
        
        eidex.ensure_db()
        
        with open(gitignore_path, "r") as f:
            content = f.read()
            # Should only appear once
            assert content.count(".eidex/") == 1

    def test_get_current_branch(self):
        """Test getting current branch."""
        branch = eidex.get_current_branch()
        assert branch == "main"  # Default branch name

    def test_get_current_branch_outside_git(self):
        """Test error when not in git repository."""
        # Mock the Git repository detection to simulate being outside a git repo
        with patch("git.Repo") as mock_repo_class:
            # Make the Repo constructor raise GitCommandError
            from git import GitCommandError
            mock_repo_class.side_effect = GitCommandError("Not a git repository")
            
            try:
                eidex.get_current_branch()
                assert False, "Should have raised ValueError"
            except ValueError as e:
                assert "Not in a Git repository" in str(e)

    def test_log_work(self):
        """Test basic logging functionality."""
        eidex.log_work("Test message")
        
        logs = eidex.fetch_branch_logs()
        assert len(logs) == 1
        assert logs[0]["message"] == "Test message"
        assert logs[0]["extra"] is None

    def test_log_work_with_extra(self):
        """Test logging with extra data."""
        extra_data = {"type": "test", "component": "database"}
        eidex.log_work("Test message", extra_data)
        
        logs = eidex.fetch_branch_logs()
        assert len(logs) == 1
        assert logs[0]["message"] == "Test message"
        assert logs[0]["extra"] == extra_data

    def test_fetch_branch_logs(self):
        """Test fetching logs for current branch."""
        eidex.log_work("Message 1")
        eidex.log_work("Message 2")
        
        logs = eidex.fetch_branch_logs()
        assert len(logs) == 2
        assert logs[0]["message"] == "Message 2"  # Newest first
        assert logs[1]["message"] == "Message 1"

    def test_fetch_branch_logs_with_limit(self):
        """Test fetching logs with limit."""
        eidex.log_work("Message 1")
        eidex.log_work("Message 2")
        eidex.log_work("Message 3")
        
        logs = eidex.fetch_branch_logs(limit=2)
        assert len(logs) == 2
        assert logs[0]["message"] == "Message 3"
        assert logs[1]["message"] == "Message 2"

    def test_fetch_branch_logs_specific_branch(self):
        """Test fetching logs for specific branch."""
        eidex.log_work("Message on main")
        
        # Create and switch to a new branch
        os.system("git checkout -b test-branch -q")
        eidex.log_work("Message on test-branch")
        
        # Switch back to main
        os.system("git checkout main -q")
        
        # Test fetching from specific branch
        logs = eidex.fetch_branch_logs(branch="test-branch")
        assert len(logs) == 1
        assert logs[0]["message"] == "Message on test-branch"

    def test_cleanup_deleted_branches(self):
        """Test cleanup of deleted branch logs."""
        # Create a branch and log to it
        os.system("git checkout -b cleanup-test -q")
        eidex.log_work("Message on cleanup-test")
        
        # Switch back to main
        os.system("git checkout main -q")
        
        # Delete the branch
        os.system("git branch -D cleanup-test -q")
        
        # Cleanup should remove logs from deleted branch
        deleted_count = eidex.cleanup_deleted_branches()
        assert deleted_count == 1

    def test_prune_old_logs(self):
        """Test pruning of old logs."""
        # Log some messages
        eidex.log_work("Recent message")
        
        # Mock the database to simulate old logs
        with patch("eidex.database.get_db_path") as mock_db_path:
            mock_db_path.return_value = os.path.join(self.temp_dir, ".eidex", ".eidex-logs.db")
            
            # Create a mock database with old logs
            import sqlite3
            conn = sqlite3.connect(mock_db_path.return_value)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO logs (timestamp, branch, message, extra) 
                VALUES (datetime('now', '-100 days'), 'main', 'Old message', NULL)
            """)
            conn.commit()
            conn.close()
            
            # Prune logs older than 90 days
            deleted_count = eidex.prune_old_logs(90)
            assert deleted_count == 1
