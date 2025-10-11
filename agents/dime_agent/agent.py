"""
Dime Agent Implementation

Main ADK agent for content creation workflows.
This agent coordinates research and writing for political liberation content.
"""

from google.adk.agents import SequentialAgent, LlmAgent
from google.adk.tools.function_tool import FunctionTool


def research_topic(topic: str) -> dict:
    """Research a topic for content creation."""
    return {
        "status": "success",
        "research": f"Research data for {topic}",
        "sources": ["example.com", "research.org"],
        "key_points": ["Point 1", "Point 2", "Point 3"],
    }


def write_content(research_data: dict) -> dict:
    """Write content based on research."""
    return {
        "status": "success",
        "content": f"Article based on {research_data}",
        "word_count": 1200,
        "sections": ["Introduction", "Analysis", "Conclusion"],
    }


# Create individual agents
researcher_agent = LlmAgent(
    name="researcher",
    model="gemini-2.5-flash",
    instruction="Research topics related to liberation movements and political history.",
    tools=[FunctionTool(research_topic)],
)

writer_agent = LlmAgent(
    name="writer",
    model="gemini-2.5-flash",
    instruction="Write engaging articles for a general audience based on research.",
    tools=[FunctionTool(write_content)],
)

# Main agent - this will be discovered by ADK
root_agent = SequentialAgent(
    name="dime_agent",
    description="Content creation system for political liberation movement articles",
    sub_agents=[researcher_agent, writer_agent],
)
