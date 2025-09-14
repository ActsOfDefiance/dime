from google.adk.agents import LlmAgent
from dime.agents import ResearcherAgent, WriterAgent


def say_something_dumb() -> dict:
    return {"status": "success", "report": ("What time is love?")}


# Create agent instances
researcher = ResearcherAgent()
writer = WriterAgent()

author = LlmAgent(
    name="author",
    model="gemini-2.0-flash",
    instruction=(
        "You are an author for a popular political website that focuses on the history of "
        "liberation movements. Your first step is to have a researcher have a topic in depth, "
        "you then rewrite the outputs of this research into short articles designed to be read "
        "by a modern audience. The audience you are speaking to liberal, 20-40, may have a "
        "college education but probably not, with a lay interest in political history and perhaps "
        "specialize knowledge is specific causes."
    ),
)

root_agent = LlmAgent(
    name="publisher",
    model="gemini-2.0-flash",
    description="Agent that coordinates research and writing for political liberation content",
    instruction=(
        "You are the publisher of a journal which focuses on the history of liberation struggles. "
        "Your journal cares deeply about citing sources and accuracy, as such you require vigorous "
        "research to be done and on any topic before producing an article. However your target audience "
        "is the common man and so the output research needs to be condensed down into blog articles. "
    ),
    sub_agents=[researcher, writer],
)
