"""Tests for eidex.file_generators module."""

import os
import tempfile
import shutil
from unittest.mock import patch

import eidex


class TestEidexFileGenerators:
    """Test suite for file generation functionality."""

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

    def test_create_default_config(self):
        """Test create_default_config function."""
        # Test creating default config
        config_path = eidex.create_default_config()
        
        # Verify config file was created
        assert os.path.exists(config_path)
        assert config_path.endswith("eidex.toml")
        
        # Check config file content
        with open(config_path, "r") as f:
            content = f.read()
            assert "[database]" in content
            assert "[logging]" in content
            assert "[git]" in content
            assert "filename = \".eidex-logs.db\"" in content
            assert "max_logs_per_branch = 1000" in content
            assert "default_limit = 50" in content

    def test_create_ai_context_file(self):
        """Test create_ai_context_file function."""
        # Test creating AI context file
        context_path = eidex.create_ai_context_file()
        
        # Verify context file was created
        assert os.path.exists(context_path)
        assert context_path.endswith("AI_CONTEXT.md")
        
        # Check context file content
        with open(context_path, "r") as f:
            content = f.read()
            assert "# Eidex AI Agent Context" in content
            assert "## Overview" in content
            assert "## Command Summary" in content
            assert "## Instructions for AI Agents" in content

    def test_create_default_config_overwrites_existing(self):
        """Test that create_default_config overwrites existing config."""
        # Create initial config
        initial_config_path = eidex.create_default_config()
        
        # Modify the config file
        with open(initial_config_path, "w") as f:
            f.write("# Modified config\n[database]\nfilename = \"custom.db\"\n")
        
        # Recreate config
        new_config_path = eidex.create_default_config()
        
        # Verify it's the same path
        assert new_config_path == initial_config_path
        
        # Verify content was reset to defaults
        with open(new_config_path, "r") as f:
            content = f.read()
            assert "filename = \".eidex-logs.db\"" in content  # Back to default
            assert "[logging]" in content
            assert "[git]" in content

    def test_create_ai_context_file_overwrites_existing(self):
        """Test that create_ai_context_file overwrites existing context."""
        # Create initial context file
        initial_context_path = eidex.create_ai_context_file()
        
        # Modify the context file
        with open(initial_context_path, "w") as f:
            f.write("# Modified context\n## Custom Section\n")
        
        # Recreate context file
        new_context_path = eidex.create_ai_context_file()
        
        # Verify it's the same path
        assert new_context_path == initial_context_path
        
        # Verify content was reset to defaults
        with open(new_context_path, "r") as f:
            content = f.read()
            assert "# Eidex AI Agent Context" in content  # Back to default
            assert "## Overview" in content
            assert "## Command Summary" in content

    def test_ensure_eidex_directory_creation(self):
        """Test that .eidex directory is created when needed."""
        # Remove .eidex directory if it exists
        eidex_dir = os.path.join(self.temp_dir, ".eidex")
        if os.path.exists(eidex_dir):
            shutil.rmtree(eidex_dir)
        
        # Create AI context file (which should create .eidex directory)
        context_path = eidex.create_ai_context_file()
        
        # Verify .eidex directory was created
        assert os.path.exists(eidex_dir)
        assert os.path.isdir(eidex_dir)
        
        # Verify context file is in the right place
        assert os.path.realpath(os.path.dirname(context_path)) == os.path.realpath(eidex_dir)

    def test_config_file_structure(self):
        """Test that generated config file has correct structure."""
        config_path = eidex.create_default_config()
        
        with open(config_path, "r") as f:
            content = f.read()
        
        # Verify all required sections
        assert "[database]" in content
        assert "[logging]" in content
        assert "[git]" in content
        
        # Verify database section content
        assert "filename = \".eidex-logs.db\"" in content
        assert "max_logs_per_branch = 1000" in content
        assert "auto_cleanup_old_logs = true" in content
        assert "cleanup_days_threshold = 90" in content
        
        # Verify logging section content
        assert "default_limit = 50" in content
        assert "timestamp_format = \"iso\"" in content
        assert "include_branch_in_output = true" in content
        
        # Verify git section content
        assert "auto_add_to_gitignore = true" in content
        assert "gitignore_entries = [\".eidex.toml\", \".eidex/\"]" in content

    def test_ai_context_file_structure(self):
        """Test that generated AI context file has correct structure."""
        context_path = eidex.create_ai_context_file()
        
        with open(context_path, "r") as f:
            content = f.read()
        
        # Verify main sections
        assert "# Eidex AI Agent Context" in content
        assert "## Overview" in content
        assert "## Command Summary" in content
        assert "## Instructions for AI Agents" in content
        assert "## Features" in content
        assert "## Usage" in content
        assert "## Configuration" in content
        assert "## Guidelines" in content
        assert "## Error Handling" in content
        assert "## Troubleshooting" in content
        
        # Verify command table
        assert "| Command | Description | Example |" in content
        assert "log_work" in content
        assert "fetch_branch_logs" in content
        assert "init_config" in content
        # Note: create_context might not be in the current AI context file

    def test_file_permissions(self):
        """Test that generated files have appropriate permissions."""
        config_path = eidex.create_default_config()
        context_path = eidex.create_ai_context_file()
        
        # Verify files are readable
        assert os.access(config_path, os.R_OK)
        assert os.access(context_path, os.R_OK)
        
        # Verify files are writable
        assert os.access(config_path, os.W_OK)
        assert os.access(context_path, os.W_OK)

    def test_directory_structure_creation(self):
        """Test that nested directory structures are created correctly."""
        # Test creating files in a deeply nested structure
        deep_dir = os.path.join(self.temp_dir, "deep", "nested", "structure")
        os.makedirs(deep_dir, exist_ok=True)
        os.chdir(deep_dir)
        
        # Initialize git in the deep directory
        os.system("git init -q")
        os.system('git config user.name "Test User"')
        os.system('git config user.email "test@example.com"')
        os.system('git commit --allow-empty -m "Initial commit" -q')
        
        # Mock the repo root to point to the deep directory
        with patch("eidex.get_repo_root") as mock_repo:
            mock_repo.return_value = deep_dir
            
            # Create config file
            config_path = eidex.create_default_config()
            assert os.path.exists(config_path)
            
            # Create context file
            context_path = eidex.create_ai_context_file()
            assert os.path.exists(context_path)
            
            # Verify .eidex directory was created in the right place
            eidex_dir = os.path.join(deep_dir, ".eidex")
            assert os.path.exists(eidex_dir)
