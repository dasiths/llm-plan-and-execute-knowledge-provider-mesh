# Multi-Agent Event-Driven Workflows
This quickstart demonstrates how to create and orchestrate event-driven workflows with multiple autonomous agents using Dapr Agents. You'll learn how to set up agents as services, implement workflow orchestration, and enable real-time agent collaboration through pub/sub messaging.

## Prerequisites
- Python 3.10 (recommended)
- pip package manager
- AzureOpenAI API key
- Dapr CLI and Docker installed

## Environment Setup

```bash
# Create a virtual environment
python3.10 -m venv .venv

# Activate the virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Configuration

1. Create a `.env` file based on the env.sample file:

```env
AZURE_OPENAI_API_VERSION="2024-08-01-preview"
AZURE_OPENAI_API_KEY=""
AZURE_OPENAI_ENDPOINT=""
AZURE_OPENAI_DEPLOYMENT="gpt4o"
AZURE_OPENAI_MODEL_NAME="gpt-4o"
```

2. Make sure Dapr is initialized on your system:

```bash
dapr init
```

3. The quickstart includes the necessary Dapr components in the `components` directory:

- `statestore.yaml`: Agent state configuration
- `pubsub.yaml`: Pub/Sub message bus configuration
- `workflowstate.yaml`: Workflow state configuration

## Project Structure

```
components/               # Dapr configuration files
├── statestore.yaml       # State store configuration
├── pubsub.yaml           # Pub/Sub configuration
└── workflowstate.yaml    # Workflow state configuration
services/                 # Directory for agent services
├── catalog/              # Catalog agent's service
│   └── app.py            # FastAPI app for catalog
├── stock/                # Stock agent's service
│   └── app.py            # FastAPI app for stock
├── stores/               # Stores agent's service
│   └── app.py            # FastAPI app for stores
└── workflow-llm/         # LLM orchestrator
    └── app.py            # Workflow service        
dapr-llm.yaml             # Multi-App Run Template using the LLM orchestrator
```

## Examples

### Agent Service Implementation

Each agent is implemented as a separate service. Here's an example for the Catalog agent:

```python
from dapr_agents import Agent, AgentActorService
from dotenv import load_dotenv
import asyncio
import logging
import httpx

async def call_get_catalog() -> str:
    # Implementation of API call to get catalog data
    # ...

async def main():
    try:
        # Define Agent
        catalog_agent = Agent(
            role="CatalogManager",
            name="CatalogAgent",
            goal="Provide product catalog information",
            instructions=["Provide accurate product details"],
            tools=[call_get_catalog, call_get_item_description, call_find_item]
        )
        
        # Expose Agent as a Service
        catalog_service = AgentActorService(
            agent=catalog_agent,
            message_bus_name="messagepubsub",
            agents_registry_store_name="agentstatestore",
            port=8001,
        )

        await catalog_service.start()
    except Exception as e:
        print(f"Error starting service: {e}")

if __name__ == "__main__":
    load_dotenv()
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
```

Similar implementations exist for the Stock and Stores agents.

### Workflow Orchestrator Implementation

The LLM-based orchestrator manages the interaction between agents by intelligently selecting which agent should handle each task:

```python
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
```

### Running the Multi-Agent System

Run all services using the Dapr CLI:

```bash
dapr run -f dapr-llm.yaml 
```

You will see the agents collaborating to process your query, with each specialized agent handling relevant parts of the task.

The `services/workflow-llm/LLMOrchestrator_state.json` file contains the current state of the workflow. You will be able to see the reasoning steps and the output from each agent there.

## Example Queries to Try

- "Find information about the Ryobi One Plus 18V Drill and check which stores have it in stock."
- "What are the 3 closest Hardy stores to Bayswater and what items do they carry?"
- "Tell me about the Osmocote Organic Fertilizer and where I can buy it."

## Example Workflow Run

```json
{
    "instances": {
        "f11536ce3f9a4d74923f57e002a04871": {
            "input": "Find information about the Ryobi One Plus 18V Drill and check which stores have it in stock.",
            "output": "### Summary Report\n\nThe task to find information about the Ryobi One Plus 18V Drill and its stock availability has been successfully completed. Here are the key points:\n\n1. **Product Details:** \n   - The Ryobi One Plus 18V Drill was identified in the product catalog with the item code **RYB-DRILL**.\n\n2. **Stock Availability:** \n   - The drill is available in three stores with the following quantities:\n     - **Store ID 101:** 10 units\n     - **Store ID 104:** 10 units\n     - **Store ID 105:** 2 units\n\n3. **Store Information:**\n   - **Hardy Bayswater:** 200 Canterbury Rd, Bayswater VIC 3153 (Store ID 101)\n   - **Hardy Chadstone:** 345 Bay Rd, Chadstone VIC 3148 (Store ID 104)\n   - **Hardy Berwick:** 12 Bulla Rd, Berwick VIC 3806 (Store ID 105)\n\n### Final Outcome:\nThe Ryobi One Plus 18V Drill is in stock at three stores. You now have detailed product, inventory, and store information to proceed with purchase or further actions.",
            "start_time": "2025-03-25T03:49:35.433408",
            "end_time": "2025-03-25T03:51:06.009392",
            "messages": [
                {
                    "id": "85d7d9be-777c-41d7-b80f-3fe7928d3252",
                    "role": "user",
                    "content": "## Mission Briefing\n\nWe have received the following task:\n\nFind information about the Ryobi One Plus 18V Drill and check which stores have it in stock.\n\n### Team of Agents\n- CatalogAgent: CatalogManager (Goal: Provide product catalog information including item descriptions and item codes.)\n- StockAgent: StockManager (Goal: Provide inventory stock information including availability and quantities.)\n- StoresAgent: StoresManager (Goal: Provide store information like store name and address.)\n\n### Execution Plan\nHere is the structured approach the team will follow to accomplish the task:\n\n[{'step': 1, 'description': 'Obtain detailed information about the Ryobi One Plus 18V Drill, including item code from the product catalog.', 'status': 'not_started', 'substeps': None}, {'step': 2, 'description': 'Query the inventory of this item across the available stores to determine availability and quantities.', 'status': 'not_started', 'substeps': None}, {'step': 3, 'description': 'Retrieve details of stores that currently stock the item, including names and addresses.', 'status': 'not_started', 'substeps': None}]\n",
                    "timestamp": "2025-03-25T03:49:47.002906",
                    "name": "LLMOrchestrator"
                },
                {
                    "id": "1ab5d073-a663-4840-a542-33d75ec2027d",
                    "role": "user",
                    "content": "Please retrieve detailed information about the Ryobi One Plus 18V Drill, including its item code, from the product catalog.",
                    "timestamp": "2025-03-25T03:49:55.002270",
                    "name": "LLMOrchestrator"
                },
                {
                    "id": "81b756c4-0bbb-4fac-9abb-57216e5e1b51",
                    "role": "user",
                    "content": "The Ryobi One Plus 18V Drill has the following details:\n\n- **Item Description:** Ryobi One Plus 18V Drill\n- **Item Code:** RYB-DRILL\n\nThis concludes the catalog lookup for the item.",
                    "timestamp": "2025-03-25T03:50:03.002583",
                    "name": "CatalogAgent"
                },
                {
                    "id": "adecd1b9-8d55-4f7b-897e-23e6d2d5df65",
                    "role": "user",
                    "content": "Please provide the inventory stock information for the item code RYB-DRILL to determine availability and quantities.",
                    "timestamp": "2025-03-25T03:50:23.004356",
                    "name": "LLMOrchestrator"
                },
                {
                    "id": "491a05a4-bc6e-46ae-b70c-97a6821c613d",
                    "role": "user",
                    "content": "The inventory stock information for the item code **RYB-DRILL** (Ryobi One Plus 18V Drill) shows the following availability:\n\n- **Store ID 101**: Quantity available is 10.\n- **Store ID 104**: Quantity available is 10.\n- **Store ID 105**: Quantity available is 2.",
                    "timestamp": "2025-03-25T03:50:29.002288",
                    "name": "StockAgent"
                },
                {
                    "id": "a6dc76f2-6d12-4c97-a18b-c90eebf91619",
                    "role": "user",
                    "content": "Please provide store details, including names and addresses, for Store IDs 101, 104, and 105.",
                    "timestamp": "2025-03-25T03:50:45.002150",
                    "name": "LLMOrchestrator"
                },
                {
                    "id": "6d282768-4265-46d4-928f-5fbe52acf480",
                    "role": "user",
                    "content": "Here are the store details for the locations that stock the Ryobi One Plus 18V Drill:\n\n1. **Store ID 101**\n   - **Store Name:** Hardy Bayswater\n   - **Address:** 200 Canterbury Rd, Bayswater VIC 3153\n\n2. **Store ID 104**\n   - **Store Name:** Hardy Chadstone\n   - **Address:** 345 Bay Rd, Chadstone VIC 3148\n\n3. **Store ID 105**\n   - **Store Name:** Hardy Berwick\n   - **Address:** 12 Bulla Rd, Berwick VIC 3806",
                    "timestamp": "2025-03-25T03:50:53.002174",
                    "name": "StoresAgent"
                }
            ],
            "last_message": {
                "id": "6d282768-4265-46d4-928f-5fbe52acf480",
                "role": "user",
                "content": "Here are the store details for the locations that stock the Ryobi One Plus 18V Drill:\n\n1. **Store ID 101**\n   - **Store Name:** Hardy Bayswater\n   - **Address:** 200 Canterbury Rd, Bayswater VIC 3153\n\n2. **Store ID 104**\n   - **Store Name:** Hardy Chadstone\n   - **Address:** 345 Bay Rd, Chadstone VIC 3148\n\n3. **Store ID 105**\n   - **Store Name:** Hardy Berwick\n   - **Address:** 12 Bulla Rd, Berwick VIC 3806",
                "timestamp": "2025-03-25T03:50:53.002174",
                "name": "StoresAgent"
            },
            "plan": [
                {
                    "step": 1,
                    "description": "Obtain detailed information about the Ryobi One Plus 18V Drill, including item code from the product catalog.",
                    "status": "completed",
                    "substeps": null
                },
                {
                    "step": 2,
                    "description": "Query the inventory of this item across the available stores to determine availability and quantities.",
                    "status": "completed",
                    "substeps": null
                },
                {
                    "step": 3,
                    "description": "Retrieve details of stores that currently stock the item, including names and addresses.",
                    "status": "completed",
                    "substeps": []
                }
            ],
            "task_history": [
                {
                    "agent": "CatalogAgent",
                    "step": 1,
                    "substep": null,
                    "result": "The Ryobi One Plus 18V Drill has the following details:\n\n- **Item Description:** Ryobi One Plus 18V Drill\n- **Item Code:** RYB-DRILL\n\nThis concludes the catalog lookup for the item.",
                    "timestamp": "2025-03-25T03:50:03.007422"
                },
                {
                    "agent": "StockAgent",
                    "step": 2,
                    "substep": null,
                    "result": "The inventory stock information for the item code **RYB-DRILL** (Ryobi One Plus 18V Drill) shows the following availability:\n\n- **Store ID 101**: Quantity available is 10.\n- **Store ID 104**: Quantity available is 10.\n- **Store ID 105**: Quantity available is 2.",
                    "timestamp": "2025-03-25T03:50:29.007486"
                },
                {
                    "agent": "StoresAgent",
                    "step": 3,
                    "substep": null,
                    "result": "Here are the store details for the locations that stock the Ryobi One Plus 18V Drill:\n\n1. **Store ID 101**\n   - **Store Name:** Hardy Bayswater\n   - **Address:** 200 Canterbury Rd, Bayswater VIC 3153\n\n2. **Store ID 104**\n   - **Store Name:** Hardy Chadstone\n   - **Address:** 345 Bay Rd, Chadstone VIC 3148\n\n3. **Store ID 105**\n   - **Store Name:** Hardy Berwick\n   - **Address:** 12 Bulla Rd, Berwick VIC 3806",
                    "timestamp": "2025-03-25T03:50:53.007111"
                }
            ]
        }
    }
}
```

## Key Concepts
- **Agent Service**: Stateful service exposing an agent via API endpoints with independent lifecycle management
- **Pub/Sub Messaging**: Event-driven communication between agents for real-time collaboration
- **State Store**: Persistent storage for both agent registration and conversational memory
- **Actor Model**: Self-contained, sequential message processing via Dapr's Virtual Actor pattern
- **Workflow Orchestration**: Coordinating agent interactions in a durable and resilient manner
- **Tool Use**: Agents' ability to invoke external functions and APIs to accomplish specific tasks, with execution details visible in workflow state files

## Monitoring and Observability
1. **Console Logs**: Monitor real-time workflow execution and agent interactions
2. **Dapr Dashboard**: View components, configurations and service details at http://localhost:8080/
3. **Zipkin Tracing**: Access distributed tracing at http://localhost:9411/zipkin/
4. **Dapr Metrics**: Access agent performance metrics via (ex: CatalogApp) http://localhost:6001/metrics when configured

## Next Steps

After completing this quickstart, you can:

- Add more agents to the workflow (e.g., a Stock Agent specifically for inventory levels)
- Extend agents with custom tools
- Deploy agents and Dapr to a Kubernetes cluster. For more information on read [Deploy Dapr on a Kubernetes cluster](https://docs.dapr.io/operations/hosting/kubernetes/kubernetes-deploy)
- Check out the [Cookbooks](../../cookbook/)

## Known Issues

- If you run into weird issues with "state" try running the `make reset_dapr` command.
- The [Dapr `@tool` decorator](https://github.com/dapr/dapr-agents/blob/main/quickstarts/03-agent-tool-call/weather_tools.py) doesn't seem to work well with async methods.

