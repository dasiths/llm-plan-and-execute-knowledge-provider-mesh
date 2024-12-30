import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.ui import Console
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
from autogen_agentchat.teams import RoundRobinGroupChat, SelectorGroupChat
from autogen_ext.models.openai import (
    OpenAIChatCompletionClient,
    AzureOpenAIChatCompletionClient,
)
from dotenv import load_dotenv
import os
import sys
import httpx


def get_model_client():
    return AzureOpenAIChatCompletionClient(
        model=os.getenv("AZURE_OPENAI_MODEL_NAME"),
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
    )


# Define tools


## weather api
async def get_weather(city: str) -> str:
    return f"The weather in {city} is 73 degrees and Sunny."


BASE_URL = "http://localhost"


# Stores API Calls
async def call_get_all_stores() -> str:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}:5000/stores")
            response.raise_for_status()
            return f"All Stores: {response.json()}"
        except httpx.HTTPStatusError as e:
            return f"Error getting all stores: {e.response.text}"


async def call_find_store_by_id(store_id: str) -> str:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}:5000/stores/{store_id}")
            response.raise_for_status()
            return f"Store {store_id}: {response.json()}"
        except httpx.HTTPStatusError as e:
            return f"Error finding store by ID {store_id}: {e.response.text}"


async def call_find_closest_stores(location: str) -> str:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{BASE_URL}:5000/stores/closest", params={"location": location}
            )
            response.raise_for_status()
            return f"Closest Stores to {location}: {response.json()}"
        except httpx.HTTPStatusError as e:
            return f"Error finding closest stores: {e.response.text}"


## Catalog API Calls
async def call_get_catalog() -> str:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}:5001/catalog")
            response.raise_for_status()
            return f"Catalog: {response.json()}"
        except httpx.HTTPStatusError as e:
            return f"Error getting catalog: {e.response.text}"


async def call_get_item_description(item_code: str) -> str:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}:5001/catalog/{item_code}")
            response.raise_for_status()
            return f"Item {item_code}: {response.json()}"
        except httpx.HTTPStatusError as e:
            return f"Error getting item description: {e.response.text}"


## Stock API Calls
async def call_get_stock_level(store_id: str, item_code: str) -> str:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}:5002/stock/{store_id}/{item_code}")
            response.raise_for_status()
            return f"Stock at Store {store_id} for Item {item_code}: {response.json()}"
        except httpx.HTTPStatusError as e:
            return f"Error getting stock level: {e.response.text}"


async def call_find_available_stock(item_code: str) -> str:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}:5002/stock/available/{item_code}")
            response.raise_for_status()
            return f"Available Stock for Item {item_code}: {response.json()}"
        except httpx.HTTPStatusError as e:
            return f"Error finding available stock: {e.response.text}"


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
            """,
    )

    stores_agent = AssistantAgent(
        name="stores_agent",
        model_client=get_model_client(),
        tools=[call_get_all_stores, call_find_store_by_id, call_find_closest_stores],
        system_message="""
            You are a stores agent.
            You provide store information using the stores tool.
            You can only make one request at a time.
            You only have the get_all_stores, find_store_by_id and call_find_closest_stores tools.
            """,
    )

    catalog_agent = AssistantAgent(
        name="catalog_agent",
        model_client=get_model_client(),
        tools=[call_get_catalog, call_get_item_description],
        system_message="""
            You are a catalog agent.
            You provide catalog information using the catalog tool.
            You can only make one request at a time.
            You only have the get_catalog and get_item_description tools.
            """,
    )

    stock_agent = AssistantAgent(
        name="stock_agent",
        model_client=get_model_client(),
        tools=[call_get_stock_level, call_find_available_stock],
        system_message="""
            You are a stock agent.
            You provide stock information using the stock tool.
            You can only make one request at a time.
            You only have the get_stock_level and find_available_stock tools.
            """,
    )

    # Define termination condition
    text_mention_termination = TextMentionTermination("TERMINATE")
    max_messages_termination = MaxMessageTermination(max_messages=25)
    termination = text_mention_termination | max_messages_termination

    # Define a team
    # https://microsoft.github.io/autogen/0.2/docs/tutorial/conversation-patterns
    # https://microsoft.github.io/autogen/dev/user-guide/agentchat-user-guide/tutorial/selector-group-chat.html
    agent_team = SelectorGroupChat(
        [planning_agent, weather_agent, stores_agent, catalog_agent, stock_agent],
        model_client=get_model_client(),
        termination_condition=termination,
    )

    # Run the team and stream messages to the console
    while True:
        user_input = await asyncio.get_event_loop().run_in_executor(
            None, input, "Enter a message for the agent: "
        )  # Unless you do input this way, message processing is blocked while waiting for input

        if not user_input or user_input.lower() == "exit":
            break

        stream = agent_team.run_stream(
            task=user_input
        )  # what's the weather in New York?
        await Console(stream)


load_dotenv(dotenv_path=".env", override=True)
asyncio.run(main())
