# Multi-Agent Event-Driven Workflows
This quickstart demonstrates how to create and orchestrate event-driven workflows with multiple autonomous agents using Dapr Agents. You'll learn how to set up agents as services, implement workflow orchestration, and enable real-time agent collaboration through pub/sub messaging.

## Prerequisites
- Python 3.10 (recommended)
- pip package manager
- OpenAI API key
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

1. Create a `.env` file for your API keys:

```env
OPENAI_API_KEY=your_api_key_here
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

Similar implementations exist for the Wizard and Stores agents.

### Workflow Orchestrator Implementation

The LLM-based orchestrator manages the interaction between agents by intelligently selecting which agent should handle each task:

```python
from dapr_agents import LLMOrchestrator
from dotenv import load_dotenv
import asyncio
import logging

async def main():
    try:
        llm_workflow_service = LLMOrchestrator(
            name="LLMOrchestrator",
            message_bus_name="messagepubsub",
            state_store_name="workflowstatestore",
            state_key="workflow_state",
            agents_registry_store_name="agentstatestore",
            agents_registry_key="agents_registry",
            service_port=8004,
            max_iterations=5
        )
        await llm_workflow_service.start()
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

## Example Queries to Try

- "Find information about the Ryobi One Plus 18V Drill and check which stores have it in stock."
- "What are the 3 closest Hardy stores to Bayswater and what items do they carry?"
- "Tell me about the Osmocote Organic Fertilizer and where I can buy it."

## Key Concepts
- **Agent Service**: Stateful service exposing an agent via API endpoints with independent lifecycle management
- **Pub/Sub Messaging**: Event-driven communication between agents for real-time collaboration
- **State Store**: Persistent storage for both agent registration and conversational memory
- **Actor Model**: Self-contained, sequential message processing via Dapr's Virtual Actor pattern
- **Workflow Orchestration**: Coordinating agent interactions in a durable and resilient manner

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

