# Streamlit Frontend

A lightweight Streamlit UI for the AI Personal Finance Advisor.

## Run

```bash
cd FinancialAdvisor_AIAgent/frontend/streamlit_app
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Open the browser (Streamlit prints the local URL). In the sidebar, set:
- API URL: `http://127.0.0.1:8001`
- Bearer Token: `dev-token`

## Pages
- Expenses: add expense, view recent, summary charts, patterns
- Portfolio: shows portfolio analysis
- Forecast: financial forecast output
- Advice: quick AI advice

This UI calls the existing FastAPI endpoints and assumes your backend/Django DB are running.

