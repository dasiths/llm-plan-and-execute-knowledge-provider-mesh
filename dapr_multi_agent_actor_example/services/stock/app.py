from dapr_agents import Agent, AgentActorService
from dapr_agents.llm.openai.chat import OpenAIChatClient
from dotenv import load_dotenv
import asyncio
import logging
import os
import httpx

BASE_URL = "http://localhost"


# Stock API Calls
async def call_get_stock_level(store_id: str, item_code: str) -> str:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}:5002/stock/qty/{store_id}/{item_code}")
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
            role="Stock Manager",
            name="Stock Agent",
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