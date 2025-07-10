from agent.state import AgentState
from agent.prompts import RAG_PROMPT
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv

load_dotenv()

def retrieve_documents(state: AgentState):
    question = state.messages[-1].content

    embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")
    vector_store = Chroma(
        collection_name="rag-chroma",
        embedding_function=embedding_model,
        persist_directory="./data/chromadb"
    )

    retriever = vector_store.as_retriever()
    documents = retriever.invoke(
        str(question),
        k=10
    )

    # Sort documents by start_index (ascending), with start_index=-1 at the end
    sorted_documents = sorted(documents, key=lambda doc: (
        doc.metadata.get('start_index', -1) == -1,
        doc.metadata.get('start_index', -1)
    ))

    return {"documents": sorted_documents}

def generate_response(state: AgentState):
    question = state.messages[-1].content
    documents = state.documents

    if documents:
        formatted_docs = "\n\n".join(doc.page_content for doc in documents)
    else:
        formatted_docs = ""
    
    rag_prompt_formatted = RAG_PROMPT.format(context=formatted_docs, question=question)
    messages = [
        SystemMessage(content=rag_prompt_formatted),
        HumanMessage(content=question)
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