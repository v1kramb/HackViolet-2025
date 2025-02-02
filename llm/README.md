# Setting up server.py
- pip install -r requirements.txt
- Configure LangSmith and OpenAI API keys
- Launch Redis service
- Start uvicorn server: uvicorn server:app --host 0.0.0.0 --port 8000 --reload