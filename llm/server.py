from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import openai
import json
import asyncio
import os
import redis.asyncio as redis
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langgraph.graph import START, StateGraph
from langchain import hub
from typing_extensions import List, TypedDict

# Envinronmental variables
os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_API_KEY"] = "..."
os.environ["OPENAI_API_KEY"] = "..."

# Initialize LLM and Vector Store
llm = ChatOpenAI(model="gpt-4o-mini", streaming=True)  # async mode
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
vector_store = InMemoryVectorStore(embeddings)

# Define RAG Prompt
prompt = hub.pull("rlm/rag-prompt")

# Define State for StateGraph
class State(TypedDict):
    question: str
    context: List[Document]
    answer: str

# Define Async Retrieval Step
async def retrieve(state: State):
    retrieved_docs = await asyncio.to_thread(vector_store.similarity_search, state["question"])
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

# Runs RAG on locally stored documents for each of the 50 states
filepath = "../legislation_data/state_data"
loader = DirectoryLoader(filepath, glob='**/*.txt', loader_cls=TextLoader)
docs = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
all_splits = text_splitter.split_documents(docs)
_ = vector_store.add_documents(documents=all_splits)


# Connect to Redis
redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)


STATE_ABBREVIATIONS = {
    'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas', 'CA': 'California',
    'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware', 'FL': 'Florida', 'GA': 'Georgia',
    'HI': 'Hawaii', 'ID': 'Idaho', 'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa',
    'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
    'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi', 'MO': 'Missouri',
    'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada', 'NH': 'New Hampshire', 'NJ': 'New Jersey',
    'NM': 'New Mexico', 'NY': 'New York', 'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio',
    'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina',
    'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah', 'VT': 'Vermont',
    'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia', 'WI': 'Wisconsin', 'WY': 'Wyoming'
}

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
        initial_retrieval = await retrieve({"question": request.tag})
        shared_context = initial_retrieval["context"]

        # Launch async tasks for all states with shared context
        tasks = [process_state(state, request.tag, shared_context) for state in STATE_ABBREVIATIONS.values()]
        results = await asyncio.gather(*tasks)

        return {
            "tag": request.tag,
            "results": results
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))