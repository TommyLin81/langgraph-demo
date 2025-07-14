"""Agent state definition for the RAG workflow.

This module defines the state structure used throughout the RAG agent workflow,
including message handling and document storage.
"""

from typing import Annotated, Literal

from langchain_core.documents import Document
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel


class AgentState(BaseModel):
    """State model for the RAG agent workflow.

    Attributes:
        messages: List of conversation messages with automatic message handling
        documents: Retrieved documents from vector store, if any
        route_decision: Decision from routing node about whether to use RAG or direct response
    """

    messages: Annotated[list[AnyMessage], add_messages]
    documents: list[Document] | None = None
    route_decision: Literal["aws_docs", "direct_response"] | None = None
