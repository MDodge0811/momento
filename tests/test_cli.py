"""Tests for eidex.cli module."""

import os
import tempfile
import shutil
from unittest.mock import patch

import eidex


class TestEidexCLI:
    """Test suite for CLI functionality."""

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
        # Test basic logging using the installed eidex command
        result = os.system('eidex log_work "CLI test message"')
        assert result == 0

    def test_cli_log_work_with_extra(self):
        """Test CLI log_work command with extra data."""
        extra_json = '{"file": "test.py", "action": "created"}'
        result = os.system(
            f'eidex log_work "CLI test message" --extra \'{extra_json}\''
        )
        assert result == 0

    def test_cli_fetch_branch_logs(self):
        """Test CLI fetch_branch_logs command."""
        # Test fetching
        result = os.system("eidex fetch_branch_logs")
        assert result == 0

    def test_cli_cleanup_deleted_branches(self):
        """Test CLI cleanup_deleted_branches command."""
        result = os.system("eidex cleanup_deleted_branches")
        assert result == 0

    def test_cli_prune_old_logs(self):
        """Test CLI prune_old_logs command."""
        result = os.system("eidex prune_old_logs 30")
        assert result == 0

    def test_cli_init_config(self):
        """Test CLI init_config command."""
        # Test creating/recreating configuration file
        result = os.system("eidex init_config")
        assert result == 0
        
        # Verify config file was created
        config_path = os.path.join(os.getcwd(), "eidex.toml")
        assert os.path.exists(config_path)
        
        # Check config file content
        with open(config_path, "r") as f:
            content = f.read()
            assert "[database]" in content
            assert "[logging]" in content
            assert "[git]" in content
            assert "filename = \".eidex-logs.db\"" in content

    def test_cli_create_context(self):
        """Test CLI create_context command."""
        # Test creating/recreating AI context file
        result = os.system("eidex create_context")
        assert result == 0
        
        # Verify AI context file was created
        context_path = os.path.join(os.getcwd(), ".eidex", "AI_CONTEXT.md")
        assert os.path.exists(context_path)
        
        # Check context file content
        with open(context_path, "r") as f:
            content = f.read()
            assert "# Eidex AI Agent Context" in content
            assert "## Overview" in content
            assert "## Command Summary" in content

    def test_cli_show_config(self):
        """Test CLI show_config command."""
        # Test showing current configuration
        result = os.system("eidex show_config")
        assert result == 0

    def test_cli_help(self):
        """Test CLI help command."""
        # Test help output - help shows but exits with error code when no command given
        result = os.system("eidex --help")
        # The help command shows but exits with error code 256 when no command is provided
        # This is expected behavior for argparse
        assert result == 256

    def test_cli_invalid_command(self):
        """Test CLI with invalid command."""
        # Test invalid command handling
        result = os.system("eidex invalid_command")
        assert result != 0  # Should fail

    def test_cli_log_work_creates_database(self):
        """Test that CLI log_work creates database when needed."""
        # Remove .eidex directory if it exists
        eidex_dir = os.path.join(self.temp_dir, ".eidex")
        if os.path.exists(eidex_dir):
            shutil.rmtree(eidex_dir)
        
        # Run CLI log_work command
        result = os.system('eidex log_work "CLI database creation test"')
        assert result == 0
        
        # Verify database was created
        db_path = os.path.join(self.temp_dir, ".eidex", ".eidex-logs.db")
        assert os.path.exists(db_path)

    def test_cli_fetch_branch_logs_with_limit(self):
        """Test CLI fetch_branch_logs with limit parameter."""
        # First log some messages
        os.system('eidex log_work "Message 1"')
        os.system('eidex log_work "Message 2"')
        os.system('eidex log_work "Message 3"')
        
        # Test fetching with limit
        result = os.system("eidex fetch_branch_logs --limit 2")
        assert result == 0

    def test_cli_fetch_branch_logs_with_branch(self):
        """Test CLI fetch_branch_logs with branch parameter."""
        # Log message on current branch
        os.system('eidex log_work "Message on main"')
        
        # Create and switch to new branch
        os.system("git checkout -b cli-test-branch -q")
        os.system('eidex log_work "Message on cli-test-branch"')
        
        # Switch back to main
        os.system("git checkout main -q")
        
        # Test fetching from specific branch
        result = os.system("eidex fetch_branch_logs --branch cli-test-branch")
        assert result == 0

    def test_cli_prune_old_logs_with_different_days(self):
        """Test CLI prune_old_logs with various day values."""
        # Test with different day values
        for days in [1, 7, 30, 90, 365]:
            result = os.system(f"eidex prune_old_logs {days}")
            assert result == 0

    def test_cli_command_output_format(self):
        """Test that CLI commands produce expected output format."""
        # Test show_config output format
        import subprocess
        result = subprocess.run(["eidex", "show_config"], 
                              capture_output=True, text=True)
        assert result.returncode == 0
        assert "Current Eidex Configuration:" in result.stdout
        assert "database" in result.stdout
        assert "logging" in result.stdout
        assert "git" in result.stdout

    def test_cli_error_handling(self):
        """Test CLI error handling for edge cases."""
        # Test with empty message
        result = os.system('eidex log_work ""')
        assert result == 0  # Should handle empty message gracefully
        
        # Test with very long message
        long_message = "x" * 1000
        result = os.system(f'eidex log_work "{long_message}"')
        assert result == 0  # Should handle long message gracefully

    def test_cli_extra_data_validation(self):
        """Test CLI extra data validation."""
        # Test with valid JSON
        valid_json = '{"type": "test", "component": "cli"}'
        result = os.system(f'eidex log_work "Valid extra data" --extra \'{valid_json}\'')
        assert result == 0
        
        # Test with invalid JSON (should fail gracefully)
        invalid_json = '{"type": "test", "component": "cli"'  # Missing closing brace
        result = os.system(f'eidex log_work "Invalid extra data" --extra \'{invalid_json}\'')
        # Should fail with error code 256 for invalid JSON
        assert result == 256
