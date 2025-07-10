from pydantic import BaseModel
from langchain_core.documents import Document
from langchain_core.messages import AnyMessage, AIMessage
from langgraph.graph.message import add_messages
from typing import Annotated

class AgentState(BaseModel):
    messages: Annotated[list[AnyMessage], add_messages]
    documents: list[Document] | None = None
