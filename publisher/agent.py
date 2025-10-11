from google.adk.agents import SequentialAgent, LlmAgent
from google.adk.tools.function_tool import FunctionTool


def say_something_dumb() -> dict:
    return {"status": "success", "report": ("What time is love?")}


# Create researcher agent
researcher = LlmAgent(
    name="researcher",
    model="gemini-2.5-flash",
    instruction=(
        "You are a researcher specializing in the history of liberation movements. "
        "Research topics thoroughly and provide accurate, well-sourced information."
    ),
    tools=[FunctionTool(say_something_dumb)],
)

# Create writer agent
writer = LlmAgent(
    name="writer",
    model="gemini-2.5-flash",
    instruction=(
        "You are a writer who transforms research into engaging articles for a general audience. "
        "Write clearly and accessibly for people aged 20-40 with varying educational backgrounds."
    ),
    tools=[FunctionTool(say_something_dumb)],
)

root_agent = SequentialAgent(
    name="publisher",
    description="Publisher agent for liberation movement content",
    instruction=(
        "You are the publisher of a journal which focuses on the history of liberation struggles. "
        "Your journal cares deeply about citing sources and accuracy, as such you require rigorous "
        "research to be done on any topic before producing an article. However your target audience "
        "is the common person and so the research needs to be condensed down into accessible blog articles."
    ),
    sub_agents=[researcher, writer],
)
