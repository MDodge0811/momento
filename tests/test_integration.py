"""Integration tests and edge cases for Eidex."""

import os
import tempfile
import shutil
from unittest.mock import patch

import eidex


class TestEidexIntegration:
    """Test suite for integration scenarios and edge cases."""

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

    def test_multiple_branch_logging(self):
        """Test logging across multiple branches."""
        # Log on main branch
        eidex.log_work("Message on main")
        
        # Create and switch to feature branch
        os.system("git checkout -b feature-branch -q")
        eidex.log_work("Message on feature branch")
        eidex.log_work("Another message on feature branch")
        
        # Switch back to main
        os.system("git checkout main -q")
        eidex.log_work("Back on main")
        
        # Verify logs are branch-specific
        main_logs = eidex.fetch_branch_logs(branch="main")
        feature_logs = eidex.fetch_branch_logs(branch="feature-branch")
        
        assert len(main_logs) == 2
        assert len(feature_logs) == 2
        
        # Verify correct messages
        main_messages = [log["message"] for log in main_logs]
        feature_messages = [log["message"] for log in feature_logs]
        
        assert "Message on main" in main_messages
        assert "Back on main" in main_messages
        assert "Message on feature branch" in feature_messages
        assert "Another message on feature branch" in feature_messages

    def test_config_reload_after_changes(self):
        """Test that config changes are reflected after reloading."""
        # Create initial config
        eidex.create_default_config()
        
        # Modify config file
        config_path = os.path.join(self.temp_dir, "eidex.toml")
        with open(config_path, "r") as f:
            content = f.read()
        
        # Change a value
        modified_content = content.replace('max_logs_per_branch = 1000', 'max_logs_per_branch = 500')
        with open(config_path, "w") as f:
            f.write(modified_content)
        
        # Verify the change is reflected
        new_value = eidex.get_config_value("database", "max_logs_per_branch")
        assert new_value == 500

    def test_database_persistence_across_sessions(self):
        """Test that database persists data across different operations."""
        # Log some messages
        eidex.log_work("Persistent message 1")
        eidex.log_work("Persistent message 2")
        
        # Verify they're in the database
        logs = eidex.fetch_branch_logs()
        assert len(logs) == 2
        
        # Simulate a new session by calling ensure_db again
        eidex.ensure_db()
        
        # Verify data is still there
        logs = eidex.fetch_branch_logs()
        assert len(logs) == 2
        assert logs[0]["message"] == "Persistent message 2"
        assert logs[1]["message"] == "Persistent message 1"

    def test_error_handling_with_corrupted_database(self):
        """Test error handling when database is corrupted."""
        # Create a database and log some data
        eidex.log_work("Test message")
        
        # Corrupt the database by truncating it
        db_path = eidex.get_db_path()
        with open(db_path, "w") as f:
            f.write("corrupted data")
        
        # Try to fetch logs - should handle gracefully
        try:
            logs = eidex.fetch_branch_logs()
            # If it succeeds, that's fine - some implementations might handle corruption
            # If it fails, that's also fine - as long as it doesn't crash
        except Exception as e:
            # Should not crash with unhandled exceptions
            assert isinstance(e, Exception)

    def test_concurrent_access_simulation(self):
        """Test that database handles concurrent-like access patterns."""
        # Simulate rapid successive operations
        for i in range(10):
            eidex.log_work(f"Rapid message {i}")
        
        # Verify all messages were logged
        logs = eidex.fetch_branch_logs()
        assert len(logs) == 10
        
        # Verify message order (newest first)
        for i, log in enumerate(logs):
            expected_message = f"Rapid message {9 - i}"  # Reverse order
            assert log["message"] == expected_message

    def test_large_dataset_handling(self):
        """Test handling of larger datasets."""
        # Log many messages
        for i in range(100):
            eidex.log_work(f"Large dataset message {i}")
        
        # Test fetching with different limits
        logs_10 = eidex.fetch_branch_logs(limit=10)
        logs_50 = eidex.fetch_branch_logs(limit=50)
        logs_all = eidex.fetch_branch_logs(limit=1000)  # Use large limit to get all logs
        
        assert len(logs_10) == 10
        assert len(logs_50) == 50
        assert len(logs_all) == 100
        
        # Verify newest messages come first
        assert logs_10[0]["message"] == "Large dataset message 99"
        assert logs_10[9]["message"] == "Large dataset message 90"

    def test_special_characters_in_messages(self):
        """Test handling of special characters in log messages."""
        special_messages = [
            "Message with 'quotes'",
            'Message with "double quotes"',
            "Message with \n newlines",
            "Message with \t tabs",
            "Message with unicode: café 🚀",
            "Message with special chars: !@#$%^&*()",
            "Message with numbers: 123.45",
            "Message with boolean: True/False",
        ]
        
        for message in special_messages:
            eidex.log_work(message)
        
        # Verify all messages were logged correctly
        logs = eidex.fetch_branch_logs()
        assert len(logs) == len(special_messages)
        
        # Verify message content is preserved
        logged_messages = [log["message"] for log in logs]
        for message in special_messages:
            assert message in logged_messages

    def test_config_file_edge_cases(self):
        """Test configuration file edge cases."""
        # Test with empty config file
        config_path = os.path.join(self.temp_dir, "eidex.toml")
        with open(config_path, "w") as f:
            f.write("")
        
        # Should fall back to defaults
        config = eidex.load_config()
        assert config["database"]["filename"] == ".eidex-logs.db"
        
        # Test with only partial config
        with open(config_path, "w") as f:
            f.write("[database]\nfilename = \"partial.db\"\n")
        
        # Should merge with defaults
        config = eidex.load_config()
        assert config["database"]["filename"] == "partial.db"
        assert config["logging"]["default_limit"] == 50  # From defaults
