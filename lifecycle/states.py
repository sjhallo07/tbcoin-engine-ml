"""
Lifecycle States Definition

Defines the different states a component can be in during its lifecycle.
"""

from enum import Enum


class LifecycleState(Enum):
    """Enum representing the lifecycle states of application components."""
    
    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    READY = "ready"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"
    
    def __str__(self):
        return self.value
    
    @property
    def is_active(self):
        """Check if the state represents an active running state."""
        return self in (LifecycleState.RUNNING, LifecycleState.READY)
    
    @property
    def is_transitional(self):
        """Check if the state is transitional."""
        return self in (
            LifecycleState.INITIALIZING,
            LifecycleState.STARTING,
            LifecycleState.STOPPING
        )
