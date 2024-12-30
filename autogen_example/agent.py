import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.ui import Console
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
from autogen_agentchat.teams import RoundRobinGroupChat, SelectorGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient, AzureOpenAIChatCompletionClient
from dotenv import load_dotenv
import os
import sys

def get_model_client():
    return AzureOpenAIChatCompletionClient(
            model=os.getenv("AZURE_OPENAI_MODEL_NAME"),
            azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        )

# Define a tool
async def get_weather(city: str) -> str:
    return f"The weather in {city} is 73 degrees and Sunny."

async def main() -> None:

    # planning agent
    planning_agent = AssistantAgent(
        "PlanningAgent",
        description="An agent for planning tasks, this agent should be the first to engage when given a new task.",
        model_client=get_model_client(),
        system_message="""
        You are a planning agent.
        Your job is to break down complex tasks into smaller, manageable subtasks.
        Your team members are:
            weather agent: gets weather information for a given city

        You only plan and delegate tasks - you do not execute them yourself.

        When assigning tasks, use this format:
        1. <agent> : <task>

        After all tasks are complete, summarize the findings and end with "TERMINATE".
        """,
    )

    # Define an tool agent
    weather_agent = AssistantAgent(
        name="weather_agent",
        model_client=get_model_client(),
        tools=[get_weather],
        system_message="""
            You are a weather agent.
            You provide weather information for a given city using the weather tool.
            You can only make one request at a time.
            You only have the weather tool.
            """
    )

    # Define termination condition
    text_mention_termination = TextMentionTermination("TERMINATE")
    max_messages_termination = MaxMessageTermination(max_messages=25)
    termination = text_mention_termination | max_messages_termination

    # Define a team
    # https://microsoft.github.io/autogen/0.2/docs/tutorial/conversation-patterns
    # https://microsoft.github.io/autogen/dev/user-guide/agentchat-user-guide/tutorial/selector-group-chat.html
    agent_team = SelectorGroupChat([planning_agent, weather_agent], model_client=get_model_client(), termination_condition=termination)

    # Run the team and stream messages to the console
    while True:
        user_input = await asyncio.get_event_loop().run_in_executor(None, input, "Enter a message for the agent: ")  # Unless you do input this way, message processing is blocked while waiting for input

        if not user_input or user_input.lower() == "exit":
            break

        stream = agent_team.run_stream(task=user_input) # what's the weather in New York?
        await Console(stream)

load_dotenv(dotenv_path=".env",override=True)
asyncio.run(main())