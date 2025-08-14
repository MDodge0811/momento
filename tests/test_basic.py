"""Basic tests for Eidex package."""

import eidex


def test_import():
    """Test that eidex can be imported successfully."""
    assert eidex is not None


def test_version():
    """Test that version is accessible."""
    assert hasattr(eidex, "__version__")
    assert eidex.__version__ == "0.1.0"


def test_public_api():
    """Test that all expected public API functions are available."""
    expected_functions = [
        "log_work",
        "fetch_branch_logs",
        "cleanup_deleted_branches",
        "prune_old_logs",
        "get_config_value",
        "load_config",
        "create_default_config",
        "create_ai_context_file",
        "ensure_db",
        "get_repo_root",
        "get_current_branch",
        "get_db_path",
    ]
    
    for func_name in expected_functions:
        assert hasattr(eidex, func_name), f"Missing function: {func_name}"
        assert callable(getattr(eidex, func_name)), f"Not callable: {func_name}"


def test_all_list():
    """Test that __all__ contains all expected functions."""
    expected_functions = [
        "cleanup_deleted_branches",
        "create_ai_context_file",
        "create_default_config",
        "fetch_branch_logs",
        "get_config_value",
        "load_config",
        "log_work",
        "prune_old_logs",
        "ensure_db",
        "get_repo_root",
        "get_current_branch",
        "get_db_path",
    ]
    
    for func_name in expected_functions:
        assert func_name in eidex.__all__, f"Missing from __all__: {func_name}"
    
    # Verify no extra functions in __all__
    assert len(eidex.__all__) == len(expected_functions)


def test_package_structure():
    """Test that the package has the expected structure."""
    # Test that we can access the main functions
    assert hasattr(eidex, "log_work")
    assert hasattr(eidex, "fetch_branch_logs")
    assert hasattr(eidex, "get_config_value")
    assert hasattr(eidex, "create_default_config")


def test_main_function():
    """Test that main function is available and callable."""
    assert hasattr(eidex, "main")
    assert callable(eidex.main)
