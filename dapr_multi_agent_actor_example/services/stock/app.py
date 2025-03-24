from dapr_agents import Agent, AgentActorService, tool
from dapr_agents.llm.openai.chat import OpenAIChatClient
from dotenv import load_dotenv
import asyncio
import logging
import os
import httpx
from pydantic import BaseModel, Field

BASE_URL = "http://localhost"


# Stock API Calls
class StockLevelSchema(BaseModel):
    store_id: str = Field(description="ID of the store to check stock")
    item_code: str = Field(description="Code of the item to check stock level for")

@tool(args_model=StockLevelSchema)
async def call_get_stock_level(store_id: str, item_code: str) -> str:
    """Get the stock level for a specific item at a specific store."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}:5002/stock/qty/{store_id}/{item_code}")
            response.raise_for_status()
            return f"Stock at Store {store_id} for Item {item_code}: {response.json()}"
        except httpx.HTTPStatusError as e:
            return f"Error getting stock level: {e.response.text}"


class ItemCodeSchema(BaseModel):
    item_code: str = Field(description="Code of the item to find available stock for")

@tool(args_model=ItemCodeSchema)
async def call_find_available_stock(item_code: str) -> str:
    """Find available stock for a specific item across all stores."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}:5002/stock/available/{item_code}")
            response.raise_for_status()
            return f"Available Stock for Item {item_code}: {response.json()}"
        except httpx.HTTPStatusError as e:
            return f"Error finding available stock: {e.response.text}"


async def main():
    try:
        llm = OpenAIChatClient(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION")
        )
        # Define Agent
        stock_agent = Agent(
            role="StockManager",
            name="StockAgent",
            goal="Provide inventory stock information including availability and quantities.",
            instructions=[
                "You are a stock agent.",
                "You provide stock information using the tools specified below.",
                "You can only make one request at a time.",
                "You only have the get_stock_level and find_available_stock tools."
            ],
            tools=[
                call_get_stock_level,
                call_find_available_stock
            ],
            llm=llm
        )

        # Expose Agent as an Actor over a Service
        stock_service = AgentActorService(
            agent=stock_agent,
            message_bus_name="messagepubsub",
            agents_registry_store_name="agentstatestore",
            agents_registry_key="agents_registry",
            service_port=8002,
        )

        await stock_service.start()
    except Exception as e:
        print(f"Error starting service: {e}")


if __name__ == "__main__":
    load_dotenv()

    logging.basicConfig(level=logging.INFO)

    asyncio.run(main())