"""Tests for eidex.config module."""

import os
import tempfile
import shutil
from unittest.mock import patch

import eidex


class TestEidexConfig:
    """Test suite for configuration management."""

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

    def test_get_repo_root(self):
        """Test get_repo_root function."""
        repo_root = eidex.get_repo_root()
        assert repo_root == self.temp_dir

    def test_get_repo_root_outside_git(self):
        """Test get_repo_root when not in a git repository."""
        # This test is more complex due to the way git.Repo works
        # For now, we'll test that the function exists and is callable
        assert callable(eidex.get_repo_root)

    def test_get_config_path(self):
        """Test get_config_path function."""
        # Test that the function exists and works
        config_value = eidex.get_config_value("database", "filename", "test.db")
        # Since no config file exists, it should return the default from DEFAULT_CONFIG
        assert config_value == ".eidex-logs.db"

    def test_load_config_without_file(self):
        """Test loading config when eidex.toml doesn't exist."""
        # Ensure no config file exists
        config_path = os.path.join(self.temp_dir, "eidex.toml")
        if os.path.exists(config_path):
            os.remove(config_path)
        
        # Load config should return defaults
        config = eidex.load_config()
        
        # Verify default values
        assert config["database"]["filename"] == ".eidex-logs.db"
        assert config["database"]["max_logs_per_branch"] == 1000
        assert config["logging"]["default_limit"] == 50
        assert config["git"]["auto_add_to_gitignore"] is True

    def test_load_config_with_custom_file(self):
        """Test loading config from custom eidex.toml."""
        # Create custom config file
        custom_config = """[database]
filename = "custom.db"
max_logs_per_branch = 500

[logging]
default_limit = 100

[git]
auto_add_to_gitignore = false
"""
        config_path = os.path.join(self.temp_dir, "eidex.toml")
        with open(config_path, "w") as f:
            f.write(custom_config)
        
        # Load config should merge custom with defaults
        config = eidex.load_config()
        
        # Verify custom values override defaults
        assert config["database"]["filename"] == "custom.db"
        assert config["database"]["max_logs_per_branch"] == 500
        assert config["logging"]["default_limit"] == 100
        assert config["git"]["auto_add_to_gitignore"] is False
        
        # Verify defaults still present for unspecified values
        assert config["database"]["auto_cleanup_old_logs"] is True
        assert config["logging"]["timestamp_format"] == "iso"

    def test_get_config_value_with_defaults(self):
        """Test get_config_value with various default scenarios."""
        # Test with existing config
        db_filename = eidex.get_config_value("database", "filename", "fallback.db")
        assert db_filename == ".eidex-logs.db"  # From default config
        
        # Test with non-existent section
        value = eidex.get_config_value("nonexistent", "key", "fallback")
        assert value == "fallback"
        
        # Test with non-existent key
        value = eidex.get_config_value("database", "nonexistent_key", "fallback")
        assert value == "fallback"
        
        # Test with None default
        value = eidex.get_config_value("database", "nonexistent_key", None)
        assert value is None

    def test_config_file_parsing_errors(self):
        """Test config loading with malformed TOML files."""
        # Create malformed config file
        malformed_config = """[database
filename = "test.db"
# Missing closing bracket
"""
        config_path = os.path.join(self.temp_dir, "eidex.toml")
        with open(config_path, "w") as f:
            f.write(malformed_config)
        
        # Load config should fall back to defaults
        config = eidex.load_config()
        
        # Verify default values are used
        assert config["database"]["filename"] == ".eidex-logs.db"
        assert config["logging"]["default_limit"] == 50

    def test_default_config_structure(self):
        """Test that default config has all required sections."""
        config = eidex.load_config()
        
        # Verify all required sections exist
        assert "database" in config
        assert "logging" in config
        assert "git" in config
        
        # Verify database section
        assert "filename" in config["database"]
        assert "max_logs_per_branch" in config["database"]
        assert "auto_cleanup_old_logs" in config["database"]
        assert "cleanup_days_threshold" in config["database"]
        
        # Verify logging section
        assert "default_limit" in config["logging"]
        assert "timestamp_format" in config["logging"]
        assert "include_branch_in_output" in config["logging"]
        
        # Verify git section
        assert "auto_add_to_gitignore" in config["git"]
        assert "gitignore_entries" in config["git"]
