"""
Tests for Lifecycle States
"""

import pytest
from lifecycle.states import LifecycleState


def test_lifecycle_state_values():
    """Test lifecycle state enum values."""
    assert str(LifecycleState.UNINITIALIZED) == "uninitialized"
    assert str(LifecycleState.RUNNING) == "running"
    assert str(LifecycleState.STOPPED) == "stopped"


def test_lifecycle_state_is_active():
    """Test is_active property."""
    assert LifecycleState.RUNNING.is_active
    assert LifecycleState.READY.is_active
    assert not LifecycleState.STOPPED.is_active
    assert not LifecycleState.ERROR.is_active


def test_lifecycle_state_is_transitional():
    """Test is_transitional property."""
    assert LifecycleState.INITIALIZING.is_transitional
    assert LifecycleState.STARTING.is_transitional
    assert LifecycleState.STOPPING.is_transitional
    assert not LifecycleState.RUNNING.is_transitional
    assert not LifecycleState.STOPPED.is_transitional
