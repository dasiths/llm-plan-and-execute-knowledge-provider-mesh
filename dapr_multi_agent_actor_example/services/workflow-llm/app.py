from dapr_agents import LLMOrchestrator
from dapr_agents.llm.openai.chat import OpenAIChatClient
from dotenv import load_dotenv
import asyncio
import logging
import os


async def main():
    try:
        llm = OpenAIChatClient(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"), # or add AZURE_OPENAI_API_KEY environment variable to .env file
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"), # or add AZURE_OPENAI_ENDPOINT environment variable to .env file
            azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION")
        )
        workflow_service = LLMOrchestrator(
            name="LLMOrchestrator",
            message_bus_name="messagepubsub",
            state_store_name="workflowstatestore",
            state_key="workflow_state",
            agents_registry_store_name="agentstatestore",
            agents_registry_key="agents_registry",
            service_port=8004,
            max_iterations=5,  # Increased to handle more complex queries involving multiple agents
            llm=llm,
            agent_selection_prompt="""
            You are an orchestrator that selects the best agent to handle a specific task.
            Available agents include:
            - Catalog Manager: For product information, item descriptions, and item codes
            - Stores Manager: For store locations, addresses, and finding nearby stores
            - Stock Manager: For inventory information, stock quantities, and product availability

            Select the most appropriate agent to handle each task step.
            """
        )

        await workflow_service.start()
    except Exception as e:
        print(f"Error starting service: {e}")


if __name__ == "__main__":
    load_dotenv()

    logging.basicConfig(level=logging.INFO)

    asyncio.run(main())