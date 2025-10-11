"""
Tests for agent functionality.

This module tests the ADK agent implementation and tools.
"""

from agents.dime_agent.agent import (
    research_topic,
    write_content,
    researcher_agent,
    writer_agent,
    root_agent,
)


def test_research_topic_tool():
    """Test research_topic tool function."""
    result = research_topic("Civil Rights Movement")

    assert result["status"] == "success"
    assert "research" in result
    assert "Civil Rights Movement" in result["research"]
    assert "sources" in result
    assert "key_points" in result


def test_write_content_tool():
    """Test write_content tool function."""
    research_data = {"topic": "Liberation Movements"}
    result = write_content(research_data)

    assert result["status"] == "success"
    assert "content" in result
    assert "word_count" in result
    assert "sections" in result


def test_researcher_agent_exists():
    """Test that researcher agent is properly configured."""
    assert researcher_agent.name == "researcher"
    assert researcher_agent.model == "gemini-2.5-flash"
    assert len(researcher_agent.tools) > 0


def test_writer_agent_exists():
    """Test that writer agent is properly configured."""
    assert writer_agent.name == "writer"
    assert writer_agent.model == "gemini-2.5-flash"
    assert len(writer_agent.tools) > 0


def test_root_agent_configuration():
    """Test that root agent is properly configured."""
    assert root_agent.name == "dime_agent"
    assert (
        root_agent.description
        == "Content creation system for political liberation movement articles"
    )
    assert len(root_agent.sub_agents) == 2
    assert researcher_agent in root_agent.sub_agents
    assert writer_agent in root_agent.sub_agents
