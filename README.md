# Tiny MCP Agent 
A minimal AI agent demonstrating **LLM reasoning**, **tool calling**, and the **Model Context Protocol (MCP)**.  
The project separates reasoning from execution:

- The LLM determines whether external information is needed.
- If a tool is required, the agent invokes an MCP tool server.
- The tool returns structured data.
- The LLM uses that data to generate the final natural-language response.

This project was built as a learning exercise before developing a larger multi-agent system for natural-language querying of healthcare databases.

## Features
- AI Hub integration (Claude/GPT/Gemini compatible)
- Tool routing via structured JSON outputs
- MCP tool server using FastMCP
- Natural language tool selection
- Two-stage reasoning (tool planning → final response)
- Modular architecture separating the model server and tool server

## Architecture
```
User
   │
   ▼
FastAPI Model Server
   │
   ▼
LLM Router
   │
   ├──────────────┐
   │              │
No Tool       Tool Required
   │              │
   ▼              ▼
Direct LLM    MCP Tool Server
 Answer            │
                   ▼
            Structured Result
                   │
                   ▼
              LLM Response
                   │
                   ▼
                Final Answer
```

## Available Tools
### Favorite Food
Returns mock favorite food information for members of a data science team.

### Search Documents
Searches a small mock hospital documentation corpus and returns relevant table descriptions.

## Tech Stack
- Python
- FastAPI
- FastMCP
- AI Hub
- Pydantic

## Concepts Explored
- LLM tool routing
- Structured JSON outputs
- Prompt engineering
- MCP client/server architecture
- Tool registration and discovery
- Agent orchestration
- Separation of reasoning and execution