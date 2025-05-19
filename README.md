# FastAPI Basic Project

This is a basic FastAPI project with two API endpoints:
- `/hello`: Returns a hello message.
- `/goodbye`: Returns a goodbye message.

## Setup

1. Install dependencies:
   ```zsh
   pip install -r requirements.txt
   ```

2. Run the FastAPI server:
   ```zsh
   uvicorn main:app --reload
   ```

Visit [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) for the interactive API documentation.
