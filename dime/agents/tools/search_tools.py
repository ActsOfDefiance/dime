"""
Web search tools for agents.

Provides a Google Search grounding tool for the ResearcherAgent.
Falls back to a stub if the ADK GoogleSearchTool is unavailable.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def make_search_tool() -> object:
    """Create a web search tool for research agents.

    Attempts to use ADK's built-in GoogleSearchTool for grounding.
    Falls back to a stub implementation if unavailable.
    """
    try:
        from google.adk.tools.google_search_tool import GoogleSearchTool  # pyright: ignore[reportMissingImports]

        return GoogleSearchTool()
    except (ImportError, Exception):
        logger.warning(
            "GoogleSearchTool unavailable — using stub search tool. "
            "Set up Grounding with Google Search for production use."
        )
        return _stub_search


def _stub_search(query: str) -> str:
    """Search the web for information on a topic.

    Args:
        query: The search query string.

    Returns:
        Search results as text. In production this uses Google Search
        grounding; this stub returns a placeholder.
    """
    return (
        f"[Search stub] No live search available. Query was: '{query}'. "
        "The agent should note that search results are unavailable and "
        "flag this as a gap in the research."
    )
