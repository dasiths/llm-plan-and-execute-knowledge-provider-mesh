# Agentic Workflows With Planners

## Introduction

This repository demonstrates two different approaches to implementing agentic workflows that connect to external knowledge sources:

1. **LangChain Plan and Execute**: A single-agent workflow using LangChain's Plan and Execute framework to connect to external knowledge providers via a REST API.

2. **AutoGen Selector Group Chat**: A multi-agent workflow using AutoGen's SelectorGroupChat to orchestrate specialized agents that interact with external systems. This example showcases integration with Model Context Protocol (MCP) servers for file system operations and Jira issue management.

Both examples show how to leverage Large Language Models (LLMs) to plan and reason over external data through API integrations, allowing agents to retrieve and process information from various sources.

## Repository Structure

- `/langchain_plan_and_execute_example/`: Single-agent example using LangChain's Plan and Execute pattern
- `/autogen_selector_group_chat_example/`: Multi-agent example using AutoGen's group chat with MCP server integration
