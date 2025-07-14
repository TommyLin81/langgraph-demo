"""RAG agent graph implementation using LangGraph.

This module defines the main workflow for a Retrieval-Augmented Generation (RAG) agent
that retrieves relevant documents from a vector store and generates responses using LLM.
"""

from typing import Literal, cast

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_openai import OpenAIEmbeddings
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel

from agent.prompts import DIRECT_RESPONSE_PROMPT, RAG_PROMPT, ROUTING_PROMPT
from agent.state import AgentState

load_dotenv()


class RoutingResponse(BaseModel):
    """Response model for routing decisions."""

    decision: Literal["aws_docs", "direct_response"]


def route_question(state: AgentState) -> dict[str, str]:
    """Route the user's question to determine if it needs RAG or direct response.

    Args:
        state: Current agent state containing messages

    Returns:
        dict: Updated state with routing decision
    """
    question = state.messages[-1].content

    routing_prompt_formatted = ROUTING_PROMPT.format(question=question)
    messages = [
        SystemMessage(content=routing_prompt_formatted),
        HumanMessage(content=question),
    ]

    llm = init_chat_model(
        model="openai:gpt-4o-mini",
        temperature=0,
    ).with_structured_output(RoutingResponse)

    response = cast(RoutingResponse, llm.invoke(messages))

    return {"route_decision": response.decision}


def retrieve_documents(state: AgentState) -> dict[str, list[Document]]:
    """Retrieve relevant documents from vector store based on the user's question.

    Args:
        state: Current agent state containing messages and documents

    Returns:
        dict: Updated state with retrieved documents sorted by start_index
    """
    question = state.messages[-1].content

    embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")
    vector_store = Chroma(
        collection_name="rag-chroma",
        embedding_function=embedding_model,
        persist_directory="./data/chromadb",
    )

    retriever = vector_store.as_retriever()
    documents = retriever.invoke(str(question), k=10)

    # Sort documents by start_index (ascending), with start_index=-1 at the end
    sorted_documents = sorted(
        documents,
        key=lambda doc: (
            doc.metadata.get("start_index", -1) == -1,
            doc.metadata.get("start_index", -1),
        ),
    )

    return {"documents": sorted_documents}


def generate_response(state: AgentState) -> dict[str, list[BaseMessage]]:
    """Generate a response using LLM based on retrieved documents and user question.

    Args:
        state: Current agent state containing messages and documents

    Returns:
        dict: Updated state with LLM response message
    """
    question = state.messages[-1].content
    documents = state.documents

    if documents:
        formatted_docs_list = []
        unique_sources = {}  # Track unique sources: {url: title}

        for i, doc in enumerate(documents):
            source_url = doc.metadata.get("source", "")
            title = doc.metadata.get("title", f"Document {i + 1}")

            if source_url and source_url not in unique_sources:
                unique_sources[source_url] = title

            doc_header = f"**Document {i + 1}**"
            if source_url:
                doc_header += f" - [{title}]({source_url})"

            formatted_doc = f"{doc_header}\n{doc.page_content}"
            formatted_docs_list.append(formatted_doc)

        unique_sources_text = ""
        if unique_sources:
            sources_list = [
                f"- [{title}]({url})" for url, title in unique_sources.items()
            ]
            unique_sources_text = "\n\nAvailable Sources:\n" + "\n".join(sources_list)

        formatted_docs = "\n\n" + "\n\n".join(formatted_docs_list) + unique_sources_text
    else:
        formatted_docs = ""

    rag_prompt_formatted = RAG_PROMPT.format(context=formatted_docs, question=question)
    messages = [
        SystemMessage(content=rag_prompt_formatted),
        HumanMessage(content=question),
    ]

    llm = init_chat_model(
        model="openai:gpt-4o-mini",
        temperature=0,
    )
    response = llm.invoke(messages)

    return {"messages": [response]}


def direct_response(state: AgentState) -> dict[str, list[BaseMessage]]:
    """Generate a direct response for non-AWS questions without RAG.

    Args:
        state: Current agent state containing messages

    Returns:
        dict: Updated state with LLM response message
    """
    question = state.messages[-1].content

    direct_prompt_formatted = DIRECT_RESPONSE_PROMPT.format(question=question)
    messages = [
        SystemMessage(content=direct_prompt_formatted),
        HumanMessage(content=question),
    ]

    llm = init_chat_model(
        model="openai:gpt-4o-mini",
        temperature=0,
    )
    response = llm.invoke(messages)

    return {"messages": [response]}


def decide_route(state: AgentState) -> str:
    """Conditional edge function to determine next node based on routing decision.

    Args:
        state: Current agent state with route_decision

    Returns:
        str: Next node name based on routing decision
    """
    if state.route_decision == "aws_docs":
        return "retrieve_documents"
    elif state.route_decision == "direct_response":
        return "direct_response"
    else:
        # This should never happen with structured output, but added for safety
        raise ValueError(f"Invalid route_decision: {state.route_decision}")


workflow = StateGraph(AgentState)
workflow.add_node("route_question", route_question)
workflow.add_node("retrieve_documents", retrieve_documents)
workflow.add_node("generate_response", generate_response)
workflow.add_node("direct_response", direct_response)

# Start with routing the question
workflow.add_edge(START, "route_question")

# Conditional routing based on question type
workflow.add_conditional_edges(
    "route_question",
    decide_route,
    {
        "retrieve_documents": "retrieve_documents",
        "direct_response": "direct_response",
    },
)

# RAG workflow: retrieve -> generate
workflow.add_edge("retrieve_documents", "generate_response")

# Both paths end at END
workflow.add_edge("generate_response", END)
workflow.add_edge("direct_response", END)

graph = workflow.compile()
