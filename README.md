# Agentic Workflows With Planners

## Introduction

This repository demonstrates four different approaches to implementing agentic workflows that connect to external knowledge sources:

1. **LangChain Plan and Execute**: A single-agent workflow using LangChain's [Plan and Execute](https://github.com/langchain-ai/langchain/blob/4852ab8d0a756700c2b2645baa53498ddde04040/cookbook/plan_and_execute_agent.ipynb) agent to connect to external knowledge providers via a REST API.

2. **AutoGen Selector Group Chat**: A multi-agent workflow using AutoGen's [SelectorGroupChat](https://microsoft.github.io/autogen/stable//user-guide/agentchat-user-guide/selector-group-chat.html) to orchestrate specialized agents that interact with external systems. This example showcases integration with Model Context Protocol (MCP) servers for file system operations and Jira issue management.

3. **Dapr Multi-Agent Virtual Actors**: An event-driven multi-agent workflow using Dapr's virtual actor model in [Dapr Agents](https://github.com/dapr/dapr-agents) to implement autonomous agents as microservices that collaborate through pub/sub messaging. This example demonstrates how to build resilient, distributed agent systems with state persistence and message-based coordination. It makes use of the [LLM based coordinator](https://github.com/dapr/dapr-agents/blob/main/docs/concepts/agents.md#llm-based-workflow) to plan.

4. **Dapr Multi-Agent Workflow**: An alternative implementation of event-driven multi-agent workflow using [Dapr Workflows](https://docs.dapr.io/developing-applications/building-blocks/workflow/workflow-overview/), which provides a simpler programming model while still leveraging pub/sub messaging for agent communication.

All examples show how to leverage Large Language Models (LLMs) to plan and reason over external data through API integrations, allowing agents to retrieve and process information from various sources.

A "knowledge provider" is a wrapper around an existing API or data source that exposes that to the Agent in a curated fashion.

## Repository Structure

- `/langchain_plan_and_execute_example/`: Single-agent example using LangChain's Plan and Execute pattern
- `/autogen_selector_group_chat_example/`: Multi-agent example using AutoGen's group chat with MCP server integration
- `/dapr_multi_agent_actor_example/`: Event-driven multi-agent workflow using Dapr's virtual actor model and pub/sub messaging
- `/dapr_multi_agent_workflow_example/`: Event-driven multi-agent workflow using Dapr workflows with pub/sub messaging
