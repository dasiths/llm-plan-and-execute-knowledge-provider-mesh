# AutoGen Selector Group Chat Example with Knowledge Providers

## Introduction

This example demonstrates using AutoGen's [SelectorGroupChat](https://microsoft.github.io/autogen/stable//user-guide/agentchat-user-guide/selector-group-chat.html) to orchestrate specialized agents that interact with external systems. The agents can access external knowledge through API integrations and Model Context Protocol (MCP) servers. This approach enables a multi-agent workflow where each agent has specific capabilities and can be selected dynamically based on the task requirements.

## Features

- **Multi-Agent Orchestration**: Uses AutoGen's SelectorGroupChat to manage specialized agents
- **API-based Knowledge Providers**: Connects to REST APIs for:
  - Store information (locations, details)
  - Catalog information (product descriptions, item codes)
  - Stock information (availability, quantities)
- **MCP Server Integration**: [Integrates with Model Context Protocol servers](https://microsoft.github.io/autogen/stable//reference/python/autogen_ext.tools.mcp.html) for:
  - [File system operations](https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem) (reading/writing files)
  - [Jira issue management](https://github.com/1broseidon/mcp-jira-server) (creating, updating, listing issues)
- **Task Planning**: Includes a dedicated planning agent that coordinates work across the team

## Prerequisites

- Jira account with API access (for Jira integration)

## :keyboard: How To Run It

1. Create a `.env` file based on the `.env.sample` file and populate the values. I have only tested it with `gpt-4o`.
   ```bash
   cp .env.sample .env
   # Edit .env with your credentials
   ```

2. Update the Jira configuration file with your project key.
   ```bash
   # Edit this file with your project key
   code tools/file_agent_workdir/.jira-config.json
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   git submodule update --init --recursive
   cd tools && ./install_mcp_servers.sh
   ```

4. First run the API-based knowledge providers.
   ```bash
   cd tools && python3 ./run_tools.py
   ```

5. Then, run the agents which also starts the MCP servers.
   ```bash
   python3 agents.py
   ```

## Example Use Cases

This setup can handle complex tasks that require multiple knowledge sources, such as:

- Finding stores with specific items in stock and documenting the results
- Creating Jira tickets based on inventory status
- Retrieving product information and saving it to a file
- Combining information from multiple sources to answer complex queries

## Example Conversation

You can try queries like:
```
"Find the stores with the Ryobi drill in stock and write that information to a file called stock.txt, then create a Jira issue to summarize the findings."
```

The system will:
1. Use the planning agent to break down the task
2. Query the catalog agent to find the item code for the Ryobi drill
3. Query the stock agent to check availability across stores
4. Use the file system agent to write results to stock.txt
5. Use the Jira agent to create an issue with the summary

## Troubleshooting

The file system MCP server sometimes has intermittent issues. This shouldn't stop the agent from working.