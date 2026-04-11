"""Backward-compatibility re-exports from dime.pipeline.state_machine.

The canonical state machine lives in dime/pipeline/state_machine.py.
This module re-exports symbols so existing imports in the API layer continue
to work without modification.
"""

from dime.pipeline.state_machine import (
    APPROVE_TRANSITIONS,
    VALID_TRANSITIONS,
    WORKER_TASKS,
    InvalidTransitionError,
    get_worker_task,
    is_valid_transition,
)

__all__ = [
    "APPROVE_TRANSITIONS",
    "VALID_TRANSITIONS",
    "WORKER_TASKS",
    "InvalidTransitionError",
    "get_worker_task",
    "is_valid_transition",
]
