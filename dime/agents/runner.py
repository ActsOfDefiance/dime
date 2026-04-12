"""
Agent runner helper.

Thin wrapper around ADK's Runner + InMemorySessionService that executes
an agent with a single input message and returns the final text output.
"""

from __future__ import annotations

import logging

from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

logger = logging.getLogger(__name__)

APP_NAME = "dime"
USER_ID = "worker"


async def run_agent(agent: LlmAgent, input_text: str) -> str:
    """Run an agent with a single input message and return its text output.

    Args:
        agent: A configured LlmAgent instance (with tools and instruction).
        input_text: The user message to send to the agent.

    Returns:
        The agent's final text response. Returns empty string if no text
        was produced.

    Raises:
        RuntimeError: If the agent execution fails entirely.
    """
    session_service = InMemorySessionService()
    runner = Runner(
        agent=agent,
        app_name=APP_NAME,
        session_service=session_service,
    )

    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
    )

    content = types.Content(
        role="user",
        parts=[types.Part(text=input_text)],
    )

    final_text = ""
    fallback_parts: list[str] = []
    async for event in runner.run_async(  # pyright: ignore[reportUnknownMemberType]
        user_id=USER_ID,
        session_id=session.id,
        new_message=content,
    ):
        if event.content and event.content.parts:
            event_text = "".join(
                p.text for p in event.content.parts if hasattr(p, "text") and p.text
            )
            if event_text:
                fallback_parts.append(event_text)

            if (
                hasattr(event, "is_final_response")
                and callable(event.is_final_response)
                and event.is_final_response()
            ):
                final_text += event_text

    if not final_text and fallback_parts:
        logger.warning("No final response detected — collecting all text events")
        final_text = "".join(fallback_parts)

    return final_text
