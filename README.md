# LangGraph Demo

A RAG AI Agent demo using LangGraph for intelligent question answering.

## Architecture

![LangGraph Workflow](./static/graph.png)

The application uses an intelligent routing workflow:

1. **Question Routing**: Analyzes incoming questions to determine the appropriate response strategy
2. **Document Retrieval**: Searches ChromaDB vector store for relevant documents
3. **Direct Response**: Provides immediate answers for simple, general questions
4. **Response Generation**: Generates contextual responses using retrieved documents and OpenAI's GPT-4o-mini

### Key Components

- **Vector Store**: ChromaDB with OpenAI embeddings
- **LLM**: OpenAI GPT-4o-mini for response generation
- **Graph Engine**: LangGraph for orchestrating the RAG workflow
- **State Management**: Typed state handling for messages and documents

## Prerequisites

### For Docker Compose (Recommended)

- Docker and Docker Compose
- OpenAI API key

### For Local Development

- Python 3.13+
- OpenAI API key
- uv package manager

## Getting Started

### Quick Start with Docker Compose

Start with Docker Compose:

1. **Create environment file**:

   ```bash
   cp .env.example .env
   # OPENAI_API_KEY is required
   ```

2. **Start all services**:

   ```bash
   make docker_up
   ```

   This starts the following services:

   - API Server: RAG agent (port 8123)
   - PostgreSQL: Stores conversation data and manages background tasks (port 5433)
   - Redis: Enables real-time streaming of agent responses (port 6379)

3. **Generate AWS documentation index for RAG**:

   ```bash
   make gen_aws_docs_index
   ```

4. **Access the application**:
   - API: <http://localhost:8123>
   - LangGraph Studio: <https://smith.langchain.com/studio/?baseUrl=http://localhost:8123>
   - Agent Chat UI: <https://agentchat.vercel.app/?apiUrl=http://localhost:8123&assistantId=agent>

### Local Development

#### Installation

Install dependencies using the Makefile:

```bash
make install
```

#### Configuration

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Enable LangSmith for tracing and experiment tracking
# LANGSMITH_PROJECT="LANGGRAPH-DEMO"
# LANGSMITH_API_KEY="your_langsmith_api_key_here"
# LANGSMITH_TRACING_V2=true
```

#### Development

Start the AI agent in developer mode:

```bash
make dev
```

This launches LangGraph Studio - a visual debugging interface for testing and monitoring your RAG agent.

## Project Structure

```text
├── src/
│   ├── agent/
│   │   ├── graph.py       # Main RAG workflow
│   │   ├── state.py       # State management
│   │   └── prompts.py     # LLM prompts
│   └── tools/
│       └── indexer.py     # Document indexing utilities
├── tests/
│   ├── unit_tests/        # Unit tests
│   └── integration_tests/ # Integration tests
├── deployment/
│   └── docker/            # Docker deployment configurations
├── data/                  # Vector store data
├── Makefile               # Development commands
└── langgraph.json         # LangGraph configuration
```

## Development Commands

The Makefile provides convenient commands for development, testing, and deployment.

### Quick Reference

Run `make help` to see all available commands.

```bash
# Development
make install      # Install dependencies
make dev          # Start LangGraph development server
make clean        # Clean up build artifacts

# Testing
make test         # Run unit tests
make lint         # Run code quality checks
make format       # Auto-format code

# Docker
make docker_up    # Start all services
make docker_down  # Stop services
```
