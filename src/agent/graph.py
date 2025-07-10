"""RAG agent graph implementation using LangGraph.

This module defines the main workflow for a Retrieval-Augmented Generation (RAG) agent
that retrieves relevant documents from a vector store and generates responses using LLM.
"""

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_openai import OpenAIEmbeddings
from langgraph.graph import END, START, StateGraph

from agent.prompts import RAG_PROMPT
from agent.state import AgentState

load_dotenv()


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
        formatted_docs = "\n\n".join(doc.page_content for doc in documents)
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


workflow = StateGraph(AgentState)
workflow.add_node("retrieve_documents", retrieve_documents)
workflow.add_node("generate_response", generate_response)
workflow.add_edge(START, "retrieve_documents")
workflow.add_edge("retrieve_documents", "generate_response")
workflow.add_edge("generate_response", END)

graph = workflow.compile()
