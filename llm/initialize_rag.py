import os
import asyncio
import json
from langchain_openai import ChatOpenAI #, OpenAIEmbeddings
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.graph import START, StateGraph
from langchain import hub
from langchain_core.documents import Document
from typing_extensions import List, TypedDict
from uuid import uuid4
import faiss

# Set environment variables
os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_API_KEY"] = "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"
os.environ["OPENAI_API_KEY"] = "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"

# Initialize LLM and Embeddings
llm = ChatOpenAI(model="gpt-4o-mini", streaming=True)
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

# Vector score
index = faiss.IndexFlatL2(len(embeddings.embed_query("hello world")))
vector_store = FAISS(
    embedding_function=embeddings,
    index=index,
    docstore=InMemoryDocstore(),
    index_to_docstore_id={},
)

# Define RAG Prompt
prompt = hub.pull("rlm/rag-prompt")

# Define State for StateGraph
class State(TypedDict):
    question: str
    context: List[Document]
    answer: str

# Define Async Retrieval Step
async def retrieve(state: State):
    retrieved_docs = vector_store.similarity_search(state["question"])
    return {"context": retrieved_docs}

# Define Async Generation Step
async def generate(state: State):
    docs_content = "\n\n".join(doc.page_content for doc in state["context"])
    messages = prompt.invoke({"question": state["question"], "context": docs_content})
    
    # Use async `ainvoke()` for OpenAI LLM
    response = await llm.ainvoke(messages)
    
    return {"answer": response.content}

# Compile Async StateGraph (RAG)
graph_builder = StateGraph(State).add_sequence([retrieve, generate])
graph_builder.add_edge(START, "retrieve")
graph = graph_builder.compile()

# Load and Process Documents
async def initialize_rag():
    print("Loading documents...")
    filepath = "../legislation_data/state_data2"
    loader = DirectoryLoader(filepath, glob='**/*.txt', loader_cls=TextLoader)
    docs = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    all_splits = text_splitter.split_documents(docs)

    print("Adding documents to vector store...")
    uuids = [str(uuid4()) for _ in range(len(all_splits))]
    vector_store.add_documents(documents=all_splits, ids=uuids)

    print("Saving vector store...")
    vector_store.save_local('faiss_index')

    print("RAG Initialization Complete.")

# Run Initialization
if __name__ == "__main__":
    asyncio.run(initialize_rag())