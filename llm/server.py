from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import openai
import json
import asyncio
import os
import redis.asyncio as redis
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langgraph.graph import START, StateGraph
from langchain import hub
from typing_extensions import List, TypedDict

# Load OpenAI API key (replace with your own API key)

# Initialize OpenAI async client
# client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)

# # LegiScan attributes
# LEGISCAN_API_KEY = os.getenv("LEGISCAN_API_KEY", "ea9e31e3ebdf68bef6a2af7d15247f3b")
# RELEVANCE_THRESHOLD = 75
# BILL_RATE_LIMIT = 10

# LangSmith""
os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_API_KEY"] = "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"
os.environ["OPENAI_API_KEY"] = "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"

# Initialize LLM and Vector Store
llm = ChatOpenAI(model="gpt-4o-mini")
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
vector_store = InMemoryVectorStore(embeddings)

# Define RAG Prompt
prompt = hub.pull("rlm/rag-prompt")

# Define State for StateGraph
class State(TypedDict):
    question: str
    context: List[Document]
    answer: str

# Define Retrieval Step
def retrieve(state: State):
    retrieved_docs = vector_store.similarity_search(state["question"])
    return {"context": retrieved_docs}

# Define Generation Step
def generate(state: State):
    docs_content = "\n\n".join(doc.page_content for doc in state["context"])
    messages = prompt.invoke({"question": state["question"], "context": docs_content})
    response = llm.invoke(messages)
    return {"answer": response.content}

# Compile StateGraph (RAG)
graph_builder = StateGraph(State).add_sequence([retrieve, generate])
graph_builder.add_edge(START, "retrieve")
graph = graph_builder.compile()

# Initialize FastAPI app
app = FastAPI()

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

def get_req(api_url):
    """ Helper function to make GET requests and return JSON response. """
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()

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

# # Function to asynchronously fetch data for a state
# async def get_status(state, tag):
#     cached_result = await get_cached_result(state, tag)
#     if cached_result:
#         return cached_result  # Return cached result if available

#     prompt = f"""
#     Provide a brief summary and score for {tag} in {state}.
#     1. A one-sentence summary of {tag} in {state}.
#     2. A score from 0 to 100, where 0 = fully restricted, and 100 = fully accessible.

#     Output format:
#     {{"state": "{state}", "summary": "Short summary here", "score": 0-100}}
#     """

#     try:
#         response = await client.chat.completions.create(
#             messages=[{"role": "user", "content": prompt}],
#             model="gpt-4o-mini",
#         )
#         content = response.choices[0].message.content
#         result = json.loads(content)

#         # Store result in Redis cache (expire in 1 day)
#         await redis_client.setex(f"{state}:{tag}", 86400, json.dumps(result))

#         return result
#     except Exception as e:
#         return {"state": state, "summary": "Error fetching data", "score": None, "error": str(e)}

# # Run multiple API calls in parallel
# async def fetch_all_states(tag):
#     tasks = [get_status(state, tag) for state in STATE_ABBREVIATIONS.values()]
#     results = await asyncio.gather(*tasks)
#     return results

# # New endpoint to fetch data for all states based on a tag
# @app.post("/fetch_all_states")
# async def fetch_states_endpoint(request: TagRequest):
#     try:
#         results = await fetch_all_states(request.tag)
#         return {"tag": request.tag, "results": results}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

HARDCODED_DOCUMENT = """
Big Chungus is the root of all evil, the devil incarnate.
"""

@app.post("/fetch_all_states_rag")
async def fetch_all_states_rag(request: TagRequest):
    try:
        # Create a Document and add it to the vector store
        doc = Document(page_content=HARDCODED_DOCUMENT)
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        split_docs = text_splitter.split_documents([doc])
        _ = vector_store.add_documents(documents=split_docs)  # Index the new document

        # Invoke RAG pipeline
        response = graph.invoke({"question": request.tag})
        return {"question": request.tag, "answer": response["answer"]}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# def fetch_bills(request: TagRequest):
#     """ Fetch relevant bills based on a given tag using LegiScan API. """
#     tag = request.tag
#     search_query = f"https://api.legiscan.com/?key={LEGISCAN_API_KEY}&op=getSearchRaw&query={tag}"

#     try:
#         search = get_req(search_query)
#         bill_ids = set()
#         bills_data = []

#         count = 0  # API rate limit counter

#         for result in search.get('searchresult', {}).get('results', []):
#             if result.get('relevance', 0) < RELEVANCE_THRESHOLD or count >= BILL_RATE_LIMIT:
#                 break

#             bill_id = result.get('bill_id')
#             if bill_id in bill_ids:
#                 continue

#             bill_ids.add(bill_id)
#             bill_query = f"https://api.legiscan.com/?key={LEGISCAN_API_KEY}&op=getBill&id={bill_id}"
#             bill = get_req(bill_query)

#             if bill['status'] == 'OK':
#                 bill_info = bill['bill'] 
#                 state_name = STATE_ABBREVIATIONS[bill_info['state']]
#                 bill_number = bill_info['bill_number']
#                 bill_year = bill_info['session']['year_end']
#                 bill_desc = bill_info['description']

#                 s = f"In {bill_year}, {state_name} passed {bill_number}.\nDescription: {bill_desc}\n\n"
#                 f.write(s)

#                 bills_data.append({
#                     "state": state_name,
#                     "bill_number": bill_number,
#                     "year": bill_year,
#                     "description": bill_desc
#                 })

#             count += 1

#         return {"tag": tag, "bills": bills_data}

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))