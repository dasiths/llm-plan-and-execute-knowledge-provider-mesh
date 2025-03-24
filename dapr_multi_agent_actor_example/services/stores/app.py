from dapr_agents import Agent, AgentActorService, tool
from dapr_agents.llm.openai.chat import OpenAIChatClient
from dotenv import load_dotenv
import asyncio
import logging
import os
import requests
from pydantic import BaseModel, Field

BASE_URL = "http://localhost"


# Stores API Calls
@tool()
def call_get_all_stores() -> str:
    """Get information about all available stores."""
    try:
        response = requests.get(f"{BASE_URL}:5000/stores/all")
        response.raise_for_status()
        return f"All Stores: {response.json()}"
    except requests.HTTPError as e:
        return f"Error getting all stores: {e.response.text}"


class StoreIdSchema(BaseModel):
    store_id: str = Field(description="ID of the store to find")

@tool(args_model=StoreIdSchema)
def call_find_store_by_id(store_id: str) -> str:
    """Find a specific store by its ID."""
    try:
        response = requests.get(f"{BASE_URL}:5000/stores/store/{store_id}")
        response.raise_for_status()
        return f"Store {store_id}: {response.json()}"
    except requests.HTTPError as e:
        return f"Error finding store by ID {store_id}: {e.response.text}"


class LocationSchema(BaseModel):
    location: str = Field(description="Location to find stores near to")

@tool(args_model=LocationSchema)
def call_find_closest_stores(location: str) -> str:
    """Find stores closest to a specified location."""
    try:
        response = requests.get(
            f"{BASE_URL}:5000/stores/closest", params={"location": location}
        )
        response.raise_for_status()
        return f"Closest Stores to {location}: {response.json()}"
    except requests.HTTPError as e:
        return f"Error finding closest stores: {e.response.text}"

async def main():
    try:
        llm = OpenAIChatClient(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION")
        )
        # Define Agent
        stores_agent = Agent(
            role="StoresManager",
            name="StoresAgent",
            goal="Provide store information like store name and address.",
            instructions=[
                "You are a stores agent.",
                "You provide store information using the tools specified below.",
                "You can only make one request at a time.",
                "You only have the get_all_stores, find_store_by_id and call_find_closest_stores tools."
            ],
            tools=[
                call_get_all_stores,
                call_find_store_by_id,
                call_find_closest_stores
            ],
            llm=llm
        )

        # Expose Agent as an Actor over a Service
        stores_service = AgentActorService(
            agent=stores_agent,
            message_bus_name="messagepubsub",
            agents_registry_store_name="agentstatestore",
            agents_registry_key="agents_registry",
            service_port=8003,
        )

        await stores_service.start()
    except Exception as e:
        print(f"Error starting service: {e}")

if __name__ == "__main__":
    load_dotenv()

    logging.basicConfig(level=logging.INFO)

    asyncio.run(main())