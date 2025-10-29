"""
TBCoin Engine ML - Lifecycle Management System

This module provides comprehensive lifecycle management for the tbcoin engine,
including application, ML model, resource, and request lifecycle management.
"""

from .manager import LifecycleManager
from .states import LifecycleState
from .model_manager import ModelLifecycleManager
from .resource_manager import ResourceLifecycleManager
from .config import LifecycleConfig

__all__ = [
    'LifecycleManager',
    'LifecycleState',
    'ModelLifecycleManager',
    'ResourceLifecycleManager',
    'LifecycleConfig',
]

__version__ = '1.0.0'
