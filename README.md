# LangGraph Demo

A RAG (Retrieval-Augmented Generation) AI Agent demo using LangGraph that combines document retrieval with LLM generation for intelligent question answering.

## Architecture

The application implements a two-node workflow:

1. **Document Retrieval**: Uses vector similarity search to find relevant documents from a ChromaDB vector store
2. **Response Generation**: Generates contextual responses using retrieved documents and OpenAI's GPT-4o-mini

### Key Components

- **Vector Store**: ChromaDB with OpenAI embeddings for document retrieval
- **LLM**: OpenAI GPT-4o-mini for response generation
- **Graph Engine**: LangGraph for orchestrating the RAG workflow
- **State Management**: Typed state handling for messages and documents

## Prerequisites

### For Docker Compose (Recommended)

- Docker and Docker Compose
- OpenAI API key

### For Local Development

- Python 3.12+
- OpenAI API key
- uv package manager

## Getting Started

### Quick Start with Docker Compose

The fastest way to get started is using Docker Compose:

1. **Create environment file**:

   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

2. **Start all services**:

   ```bash
   make docker_up
   ```

3. **Generate AWS documentation index for RAG**:

   ```bash
   make gen_aws_docs_index
   ```

4. **Access the application**:
   - API: <http://localhost:8123>
   - LangGraph Studio: <https://smith.langchain.com/studio/?baseUrl=http://localhost:8123> (visual debugging and testing interface)
   - Agent Chat UI: <https://agentchat.vercel.app> (web frontend - connect to API at `http://localhost:8123`)
   - PostgreSQL: localhost:5433
   - Redis: localhost:6379

### Local Development

For local development without Docker:

#### Installation

Install dependencies using uv:

```bash
uv sync
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
uv run langgraph dev --port 2024
```

This will launch the LangGraph Studio interface - a visual debugging and testing environment for your RAG agent where you can inspect conversation flows, test queries, and monitor agent performance in real-time.

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
└── langgraph.json         # LangGraph configuration
```

## Usage

The RAG agent processes questions through a two-step workflow:

1. **Document Retrieval**: Searches the vector store for relevant documents based on semantic similarity
2. **Response Generation**: Uses retrieved documents as context to generate accurate, informed responses

The agent maintains conversation state and can handle follow-up questions while preserving context from previous interactions.
