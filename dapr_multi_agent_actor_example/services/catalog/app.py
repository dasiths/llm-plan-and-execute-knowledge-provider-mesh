from dapr_agents import Agent, AgentActorService, tool
from dapr_agents.llm.openai.chat import OpenAIChatClient
from dotenv import load_dotenv
import asyncio
import logging
import os
import requests
from pydantic import BaseModel, Field

BASE_URL = "http://localhost"


# Catalog API Calls
@tool()
def call_get_catalog() -> str:
    """Get the full product catalog information."""
    try:
        response = requests.get(f"{BASE_URL}:5001/catalog/all")
        response.raise_for_status()
        return f"Full Catalog: {response.json()}"
    except requests.HTTPError as e:
        return f"Error getting catalog: {e.response.text}"


class ItemCodeSchema(BaseModel):
    item_code: str = Field(description="Code of the item to get description for")

@tool(args_model=ItemCodeSchema)
def call_get_item_description(item_code: str) -> str:
    """Get detailed description of a specific item by its code."""
    try:
        response = requests.get(f"{BASE_URL}:5001/catalog/item/{item_code}")
        response.raise_for_status()
        return f"Item {item_code}: {response.json()}"
    except requests.HTTPError as e:
        return f"Error getting item description: {e.response.text}"


class QuerySchema(BaseModel):
    query: str = Field(description="Search query to find items in catalog")

@tool(args_model=QuerySchema)
def call_find_item(query: str) -> str:
    """Find items in the catalog matching a search query."""
    try:
        response = requests.get(f"{BASE_URL}:5001/catalog/search/{query}")
        response.raise_for_status()
        return f"Search Results for '{query}': {response.json()}"
    except requests.HTTPError as e:
        return f"Error finding item: {e.response.text}"


async def main():
    try:
        llm = OpenAIChatClient(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION")
        )
        # Define Agent
        catalog_agent = Agent(
            role="CatalogManager",
            name="CatalogAgent",
            goal="Provide product catalog information including item descriptions and item codes.",
            instructions=[
                "You are a catalog agent.",
                "You provide product information using the tools specified below.",
                "You can only make one request at a time.",
                "You only have the get_catalog, get_item_description and find_item tools."
            ],
            tools=[
                call_get_catalog,
                call_get_item_description,
                call_find_item
            ],
            llm=llm
        )

        # Expose Agent as an Actor over a Service
        catalog_service = AgentActorService(
            agent=catalog_agent,
            message_bus_name="messagepubsub",
            agents_registry_store_name="agentstatestore",
            agents_registry_key="agents_registry",
            service_port=8001,
        )

        await catalog_service.start()
    except Exception as e:
        print(f"Error starting service: {e}")


if __name__ == "__main__":
    load_dotenv()

    logging.basicConfig(level=logging.INFO)

    asyncio.run(main())
