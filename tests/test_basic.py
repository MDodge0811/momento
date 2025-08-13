"""
Basic tests to verify the test infrastructure is working.
"""

import pytest


def test_import():
    """Test that we can import the eidex module."""
    try:
        import eidex

        assert eidex is not None
    except ImportError as e:
        pytest.fail(f"Failed to import eidex: {e}")


def test_version():
    """Test that we can access version information."""
    import eidex

    # The library should be importable
    assert hasattr(eidex, "log_work")
    assert hasattr(eidex, "fetch_branch_logs")
    assert hasattr(eidex, "ensure_db")


def test_simple_math():
    """Simple test to verify pytest is working."""
    assert 2 + 2 == 4
    assert "hello" + " world" == "hello world"
