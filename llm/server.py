from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import openai
import json
import asyncio
import os
import redis.asyncio as redis
from langchain_openai import ChatOpenAI #, OpenAIEmbeddings
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langgraph.graph import START, StateGraph
from langchain import hub
from langchain_core.documents import Document
from typing_extensions import List, TypedDict
import faiss

STATES = [
    "Alabama", "Alaska", "Arizona", "Arkansas", "California",
    "Colorado", "Connecticut", "Delaware", "Florida", "Georgia",
    "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa",
    "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland",
    "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri",
    "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey",
    "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio",
    "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina",
    "South Dakota", "Tennessee", "Texas", "Utah", "Vermont",
    "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"
]

# Set environment variables
os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_API_KEY"] = "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"
os.environ["OPENAI_API_KEY"] = "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"

# Initialize LLM and Load Persisted Vector Store
llm = ChatOpenAI(model="gpt-4o-mini", streaming=True)
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

vector_store = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)

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

# Initialize FastAPI app
app = FastAPI()

# Connect to Redis
redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)

# Define request body
class TagRequest(BaseModel):
    tag: str

# Function to check Redis cache
async def get_cached_result(state, tag):
    key = f"{state}:{tag}"
    cached_data = await redis_client.get(key)
    if cached_data:
        return json.loads(cached_data)
    return None

# Process state's stance on tag with RAG
async def process_state(state_name: str, tag: str, context: List[Document]):
    cached_result = await get_cached_result(state_name, tag)
    if cached_result:
        return cached_result  # Return cached result if available

    prompt = f"""
        Provide a brief summary and score for {tag} in {state_name}.
        1. A one-sentence summary of {tag} in {state_name}.
        2. A score from 0 to 100, where 0 = fully restricted, and 100 = fully accessible.

        Output format:
        {{"state": "{state_name}", "summary": "Short summary here", "score": 0-100}}
        """

    try:
        response = await graph.ainvoke({"question": prompt, "context": context})
        result = json.loads(response["answer"])
        await redis_client.setex(f"{state_name}:{tag}", 86400, json.dumps(result))

        return {
            "state": state_name,
            "answer": response["answer"]
        }
    except Exception as e:
        return {
            "state": state_name,
            "error": str(e)
        }

# Runs RAG in parallel for all 50 states
@app.post("/fetch_all_states_rag_parallel")
async def fetch_all_states_rag_parallel(request: TagRequest):
    try:
        # Retrieve context for use in RAG
        #initial_retrieval = await retrieve({"question": request.tag})
        #shared_context = initial_retrieval["context"]

        # Launch async tasks for all states with shared context
        # tasks = [process_state(state, request.tag, shared_context) for state in STATES]
        tasks = [process_state(state, request.tag, []) for state in STATES]
        results = await asyncio.gather(*tasks)

        return {
            "tag": request.tag,
            "results": results
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

