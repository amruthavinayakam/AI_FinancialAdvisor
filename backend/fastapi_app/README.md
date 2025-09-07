# FastAPI App

This directory will contain the FastAPI app for AI endpoints, financial data aggregation, and integration with the AI layer.

## Next Steps
- Initialize a FastAPI app in this directory.
- Set up PostgreSQL connection (shared with Django).
- Add endpoints for AI chat, financial data, and LLM orchestration. 

## Running the FastAPI App

1. (Optional) Create and activate a virtual environment:
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```
2. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
3. Run the FastAPI app:
   ```powershell
   uvicorn main:app --reload
   ```

## Environment Variables

Create a `.env` file in this directory with your PostgreSQL and secret key settings:
```
POSTGRES_DB=your_db_name
POSTGRES_USER=your_db_user
POSTGRES_PASSWORD=your_db_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
SECRET_KEY=your_secret_key
``` 