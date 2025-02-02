from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import openai
import json
import asyncio
import os

# Load OpenAI API key (replace with your own API key)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "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")

# Initialize OpenAI async client
client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)

# Initialize FastAPI app
app = FastAPI()

# List of states
states = [
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut",
    "Delaware", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa",
    "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan",
    "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire",
    "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio",
    "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota",
    "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington", "West Virginia",
    "Wisconsin", "Wyoming"
]

# Define request body
class TagRequest(BaseModel):
    tag: str
    model: str = "gpt-4o-mini"

# Function to asynchronously fetch data for a state
async def get_status(state, tag):
    prompt = f"""
    Provide a brief summary and score for {tag} in {state}.
    1. A one-sentence summary of {tag} in {state}.
    2. A score from 0 to 100, where 0 = fully restricted, and 100 = fully accessible.

    Output format:
    {{"state": "{state}", "summary": "Short summary here", "score": 0-100}}
    """

    try:
        response = await client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="gpt-4o-mini",
        )
        content = response.choices[0].message.content
        return json.loads(content)
    except Exception as e:
        return {"state": state, "summary": "Error fetching data", "score": None, "error": str(e)}

# Run multiple API calls in parallel
async def fetch_all_states(tag):
    tasks = [get_status(state, tag) for state in states]
    results = await asyncio.gather(*tasks)
    return results

# New endpoint to fetch data for all states based on a tag
@app.post("/fetch_all_states")
async def fetch_states_endpoint(request: TagRequest):
    try:
        results = await fetch_all_states(request.tag)
        return {"tag": request.tag, "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))