"""
Agent tool factories.

Each module exports make_*() functions that create FunctionTool instances
with runtime dependencies (adapters, guides) closed over.
"""

from dime.agents.tools.filesystem_tools import (
    make_list_tool,
    make_read_tool,
    make_write_tool,
)
from dime.agents.tools.image_tools import make_image_generation_tool
from dime.agents.tools.search_tools import make_search_tool

__all__ = [
    "make_image_generation_tool",
    "make_list_tool",
    "make_read_tool",
    "make_search_tool",
    "make_write_tool",
]
