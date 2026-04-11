"""
Tests for agent prompts and agent class configuration.

Validates the 4-agent pipeline: prompt constants exist and are well-formed,
and each agent class instantiates with the correct name, model, and instruction.
"""

import pytest

from dime.agents import (
    ArtDirectorAgent,
    DimeBaseAgent,
    ImageAgent,
    PublisherAgent,
    ResearcherAgent,
    WriterAgent,
)
from dime.agents.prompts import (
    ART_DIRECTOR_PROMPT,
    IMAGE_PROMPT,
    RESEARCH_PROMPT,
    WRITER_PROMPT,
)


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

    def test_researcher_agent(self) -> None:
        """ResearcherAgent has correct name, model, and instruction."""
        agent = ResearcherAgent()
        assert agent.name == "researcher"
        assert agent.model == "gemini-2.5-flash"
        assert agent.instruction == RESEARCH_PROMPT
        assert isinstance(agent, DimeBaseAgent)

    def test_writer_agent(self) -> None:
        """WriterAgent has correct name, model, and instruction."""
        agent = WriterAgent()
        assert agent.name == "writer"
        assert agent.model == "gemini-2.5-flash"
        assert agent.instruction == WRITER_PROMPT
        assert isinstance(agent, DimeBaseAgent)

    def test_art_director_agent(self) -> None:
        """ArtDirectorAgent has correct name, model, and instruction."""
        agent = ArtDirectorAgent()
        assert agent.name == "art_director"
        assert agent.model == "gemini-2.5-flash"
        assert agent.instruction == ART_DIRECTOR_PROMPT
        assert isinstance(agent, DimeBaseAgent)

    def test_image_agent(self) -> None:
        """ImageAgent has correct name, model, and instruction."""
        agent = ImageAgent()
        assert agent.name == "image"
        assert agent.model == "gemini-2.5-flash"
        assert agent.instruction == IMAGE_PROMPT
        assert isinstance(agent, DimeBaseAgent)

    def test_publisher_agent(self) -> None:
        """PublisherAgent has correct name, model, and non-empty instruction."""
        agent = PublisherAgent()
        assert agent.name == "publisher"
        assert agent.model == "gemini-2.5-flash"
        assert isinstance(agent.instruction, str)
        assert len(agent.instruction) > 0
        assert isinstance(agent, DimeBaseAgent)

    def test_publisher_agent_accepts_sub_agents(self) -> None:
        """PublisherAgent can accept sub_agents parameter."""
        agent = PublisherAgent(sub_agents=[])
        assert agent.name == "publisher"


# --- Module exports test ---


class TestModuleExports:
    """Verify __init__.py exports are complete."""

    def test_all_agents_exported(self) -> None:
        """All agent classes are accessible from dime.agents."""
        import dime.agents

        assert hasattr(dime.agents, "ArtDirectorAgent")
        assert hasattr(dime.agents, "DimeBaseAgent")
        assert hasattr(dime.agents, "ImageAgent")
        assert hasattr(dime.agents, "PublisherAgent")
        assert hasattr(dime.agents, "ResearcherAgent")
        assert hasattr(dime.agents, "WriterAgent")

    def test_all_list_complete(self) -> None:
        """__all__ contains all expected exports."""
        from dime.agents import __all__

        expected = {
            "ArtDirectorAgent",
            "DimeBaseAgent",
            "ImageAgent",
            "PublisherAgent",
            "ResearcherAgent",
            "WriterAgent",
        }
        assert set(__all__) == expected
