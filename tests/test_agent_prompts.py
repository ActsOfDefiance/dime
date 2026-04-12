"""
Tests for agent prompts, agent class configuration, and agent tools.

Validates the 4-agent pipeline: prompt constants exist and are well-formed,
each agent class instantiates with the correct name, model, and instruction,
and tool factories produce callable tools.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

import dime.agents
from dime.agents import (
    ArtDirectorAgent,
    DimeBaseAgent,
    ImageAgent,
    PublisherAgent,
    ResearcherAgent,
    WriterAgent,
    __all__ as AGENTS_ALL,
)
from dime.agents.prompts import (
    ART_DIRECTOR_PROMPT,
    IMAGE_PROMPT,
    RESEARCH_PROMPT,
    WRITER_PROMPT,
)
from dime.agents.tools.filesystem_tools import (
    make_list_tool,
    make_read_tool,
    make_write_tool,
)
from dime.agents.tools.image_tools import make_image_generation_tool
from dime.agents.tools.search_tools import make_search_tool


# --- Prompt constant tests ---


class TestPromptConstants:
    """Verify prompt constants are non-empty and contain expected structure."""

    @pytest.mark.parametrize(
        "prompt,name",
        [
            (RESEARCH_PROMPT, "RESEARCH_PROMPT"),
            (WRITER_PROMPT, "WRITER_PROMPT"),
            (ART_DIRECTOR_PROMPT, "ART_DIRECTOR_PROMPT"),
            (IMAGE_PROMPT, "IMAGE_PROMPT"),
        ],
    )
    def test_prompt_is_nonempty_string(self, prompt: str, name: str) -> None:
        """Each prompt constant must be a non-empty string."""
        assert isinstance(prompt, str), f"{name} is not a string"
        assert len(prompt) > 100, f"{name} is too short to be a useful prompt"

    @pytest.mark.parametrize(
        "prompt,expected_sections",
        [
            (RESEARCH_PROMPT, ["## Input", "## Output", "## Constraints"]),
            (WRITER_PROMPT, ["## Input", "## Output", "## Constraints"]),
            (ART_DIRECTOR_PROMPT, ["## Input", "## Output", "## Constraints"]),
            (IMAGE_PROMPT, ["## Input", "## Output", "## Constraints"]),
        ],
    )
    def test_prompt_has_required_sections(
        self, prompt: str, expected_sections: list[str]
    ) -> None:
        """Each prompt must contain Input, Output, and Constraints sections."""
        for section in expected_sections:
            assert section in prompt, f"Missing section: {section}"

    def test_research_prompt_mentions_sources(self) -> None:
        """Research prompt must require citations/sources."""
        assert "source" in RESEARCH_PROMPT.lower()
        assert (
            "citation" in RESEARCH_PROMPT.lower() or "cite" in RESEARCH_PROMPT.lower()
        )

    def test_writer_prompt_mentions_no_fabrication(self) -> None:
        """Writer prompt must prohibit fabrication."""
        assert (
            "fabrication" in WRITER_PROMPT.lower()
            or "fabricat" in WRITER_PROMPT.lower()
        )

    def test_art_director_prompt_mentions_slots(self) -> None:
        """Art director prompt must reference image slots."""
        assert "slot" in ART_DIRECTOR_PROMPT.lower()

    def test_image_prompt_mentions_variants(self) -> None:
        """Image prompt must reference variants."""
        assert "variant" in IMAGE_PROMPT.lower()


# --- Agent class instantiation tests ---


class TestAgentInstantiation:
    """Verify each agent class instantiates with correct configuration."""

    def test_researcher_agent_default(self) -> None:
        """ResearcherAgent with no args uses RESEARCH_PROMPT as instruction."""
        agent = ResearcherAgent()
        assert agent.name == "researcher"
        assert agent.model == "gemini-2.5-flash"
        assert agent.instruction == RESEARCH_PROMPT
        assert isinstance(agent, DimeBaseAgent)

    def test_researcher_agent_with_guide(self) -> None:
        """ResearcherAgent injects content_guide into instruction."""
        guide = {"audience": "general public", "min_sources": 5}
        agent = ResearcherAgent(content_guide=guide)
        instruction = str(agent.instruction)
        assert RESEARCH_PROMPT in instruction
        assert "general public" in instruction
        assert "Content Guide" in instruction

    def test_researcher_agent_with_tools(self) -> None:
        """ResearcherAgent accepts tools parameter."""
        tool = lambda: "stub"  # noqa: E731
        agent = ResearcherAgent(tools=[tool])
        assert len(agent.tools) == 1  # pyright: ignore[reportUnknownMemberType,reportUnknownArgumentType]

    def test_writer_agent(self) -> None:
        """WriterAgent has correct name, model, and instruction."""
        agent = WriterAgent()
        assert agent.name == "writer"
        assert agent.model == "gemini-2.5-flash"
        assert agent.instruction == WRITER_PROMPT
        assert isinstance(agent, DimeBaseAgent)

    def test_writer_agent_with_guide(self) -> None:
        """WriterAgent injects content_guide into instruction."""
        guide = {"voice": "conversational"}
        agent = WriterAgent(content_guide=guide)
        assert "conversational" in str(agent.instruction)

    def test_art_director_agent(self) -> None:
        """ArtDirectorAgent has correct name, model, and instruction."""
        agent = ArtDirectorAgent()
        assert agent.name == "art_director"
        assert agent.model == "gemini-2.5-flash"
        assert agent.instruction == ART_DIRECTOR_PROMPT
        assert isinstance(agent, DimeBaseAgent)

    def test_art_director_agent_with_both_guides(self) -> None:
        """ArtDirectorAgent accepts both content_guide and style_guide."""
        agent = ArtDirectorAgent(
            content_guide={"audience": "teens"},
            style_guide={"palette": "bold"},
        )
        instruction = str(agent.instruction)
        assert "Content Guide" in instruction
        assert "Style Guide" in instruction
        assert "bold" in instruction

    def test_image_agent(self) -> None:
        """ImageAgent has correct name, model, and instruction."""
        agent = ImageAgent()
        assert agent.name == "image"
        assert agent.model == "gemini-2.5-flash"
        assert agent.instruction == IMAGE_PROMPT
        assert isinstance(agent, DimeBaseAgent)

    def test_image_agent_with_style_guide(self) -> None:
        """ImageAgent injects style_guide into instruction."""
        agent = ImageAgent(style_guide={"aesthetic": "minimalist"})
        assert "minimalist" in str(agent.instruction)

    def test_publisher_agent(self) -> None:
        """PublisherAgent is a non-LLM agent with publishing + filesystem deps."""
        mock_publishing = MagicMock()
        mock_fs = MagicMock()
        agent = PublisherAgent(publishing=mock_publishing, filesystem=mock_fs)
        assert agent._publishing is mock_publishing  # pyright: ignore[reportPrivateUsage]
        assert agent._filesystem is mock_fs  # pyright: ignore[reportPrivateUsage]


# --- Tool factory tests ---


class TestToolFactories:
    """Verify tool factories produce callable tools."""

    def test_make_read_tool(self) -> None:
        """make_read_tool returns a callable that reads from the filesystem."""
        mock_fs = MagicMock()
        mock_fs.exists.return_value = True
        mock_fs.read.return_value = "file content"
        tool = make_read_tool(mock_fs)
        result = tool("test.md")  # type: ignore[operator]
        assert result == "file content"
        mock_fs.read.assert_called_once_with("test.md")

    def test_make_read_tool_missing_file(self) -> None:
        """make_read_tool returns error message for missing files."""
        mock_fs = MagicMock()
        mock_fs.exists.return_value = False
        tool = make_read_tool(mock_fs)
        result = tool("missing.md")  # type: ignore[operator]
        assert "does not exist" in result

    def test_make_write_tool(self) -> None:
        """make_write_tool returns a callable that writes to the filesystem."""
        mock_fs = MagicMock()
        tool = make_write_tool(mock_fs)
        result = tool("out.md", "hello world")  # type: ignore[operator]
        mock_fs.write.assert_called_once_with("out.md", "hello world")
        assert "Successfully wrote" in result

    def test_make_list_tool(self) -> None:
        """make_list_tool returns a callable that lists files."""
        mock_fs = MagicMock()
        mock_fs.list.return_value = ["a.md", "b.md"]
        tool = make_list_tool(mock_fs)
        result = tool("")  # type: ignore[operator]
        assert "a.md" in result
        assert "b.md" in result

    def test_make_list_tool_empty(self) -> None:
        """make_list_tool returns message when no files found."""
        mock_fs = MagicMock()
        mock_fs.list.return_value = []
        tool = make_list_tool(mock_fs)
        result = tool("empty/")  # type: ignore[operator]
        assert "No files found" in result

    def test_make_read_tool_rejects_traversal(self) -> None:
        """make_read_tool rejects path traversal attempts."""
        mock_fs = MagicMock()
        tool = make_read_tool(mock_fs)
        result = tool("../../etc/passwd")  # type: ignore[operator]
        assert "Error" in result
        assert "escapes" in result
        mock_fs.read.assert_not_called()

    def test_make_read_tool_rejects_absolute_path(self) -> None:
        """make_read_tool rejects absolute paths."""
        mock_fs = MagicMock()
        tool = make_read_tool(mock_fs)
        result = tool("/etc/passwd")  # type: ignore[operator]
        assert "Error" in result
        mock_fs.read.assert_not_called()

    def test_make_write_tool_rejects_traversal(self) -> None:
        """make_write_tool rejects path traversal attempts."""
        mock_fs = MagicMock()
        tool = make_write_tool(mock_fs)
        result = tool("../evil.sh", "bad")  # type: ignore[operator]
        assert "Error" in result
        mock_fs.write.assert_not_called()

    def test_make_list_tool_rejects_traversal(self) -> None:
        """make_list_tool rejects path traversal attempts."""
        mock_fs = MagicMock()
        tool = make_list_tool(mock_fs)
        result = tool("../../")  # type: ignore[operator]
        assert "Error" in result
        mock_fs.list.assert_not_called()

    def test_make_search_tool(self) -> None:
        """make_search_tool returns a callable (stub or GoogleSearchTool)."""
        tool = make_search_tool()
        assert tool is not None

    def test_make_image_generation_tool(self) -> None:
        """make_image_generation_tool returns a callable stub."""
        tool = make_image_generation_tool("test-article", "hero")
        result = tool("A dramatic image", 1200, 630)  # type: ignore[operator]
        assert "test-article" in result
        assert "hero" in result


# --- Guide context formatting tests ---


class TestGuideContext:
    """Verify DimeBaseAgent.format_guide_context works correctly."""

    def test_no_guides_returns_empty(self) -> None:
        result = DimeBaseAgent.format_guide_context()
        assert result == ""

    def test_content_guide_formatted(self) -> None:
        result = DimeBaseAgent.format_guide_context(
            content_guide={"audience": "young adults"}
        )
        assert "Content Guide" in result
        assert "young adults" in result

    def test_style_guide_formatted(self) -> None:
        result = DimeBaseAgent.format_guide_context(
            style_guide={"palette": "earth tones"}
        )
        assert "Style Guide" in result
        assert "earth tones" in result

    def test_both_guides_formatted(self) -> None:
        result = DimeBaseAgent.format_guide_context(
            content_guide={"voice": "authoritative"},
            style_guide={"mood": "serious"},
        )
        assert "Content Guide" in result
        assert "Style Guide" in result


# --- Module exports test ---


class TestModuleExports:
    """Verify __init__.py exports are complete."""

    def test_all_agents_exported(self) -> None:
        """All agent classes are accessible from dime.agents."""
        assert hasattr(dime.agents, "ArtDirectorAgent")
        assert hasattr(dime.agents, "DimeBaseAgent")
        assert hasattr(dime.agents, "ImageAgent")
        assert hasattr(dime.agents, "PublisherAgent")
        assert hasattr(dime.agents, "ResearcherAgent")
        assert hasattr(dime.agents, "WriterAgent")

    def test_all_list_complete(self) -> None:
        """__all__ contains all expected exports."""
        expected = {
            "ArtDirectorAgent",
            "DimeBaseAgent",
            "ImageAgent",
            "PublisherAgent",
            "ResearcherAgent",
            "WriterAgent",
        }
        assert set(AGENTS_ALL) == expected
