import streamlit as st
import requests
import pandas as pd
import altair as alt


def get_settings():
    if "api_url" not in st.session_state:
        st.session_state.api_url = "http://127.0.0.1:8001"
    if "api_token" not in st.session_state:
        st.session_state.api_token = "dev-token"
    return st.session_state.api_url, st.session_state.api_token


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def api_get(path: str):
    base_url, token = get_settings()
    url = f"{base_url}{path}"
    resp = requests.get(url, headers=auth_headers(token))
    resp.raise_for_status()
    return resp.json()


def api_post(path: str, payload: dict):
    base_url, token = get_settings()
    url = f"{base_url}{path}"
    resp = requests.post(url, json=payload, headers={
        **auth_headers(token), "accept": "application/json", "Content-Type": "application/json"
    })
    # Surface 4xx details nicely
    if resp.status_code >= 400:
        try:
            st.error(resp.json())
        except Exception:
            st.error(resp.text)
        resp.raise_for_status()
    return resp.json()


st.set_page_config(page_title="AI Finance Advisor", layout="wide")

st.sidebar.title("Settings")
api_url, api_token = get_settings()
st.session_state.api_url = st.sidebar.text_input("API URL", api_url)
st.session_state.api_token = st.sidebar.text_input("Bearer Token", api_token)

page = st.sidebar.radio("Navigation", ["Expenses", "Portfolio", "Forecast", "Advice"]) 

st.title("AI Personal Finance Advisor")

if page == "Expenses":
    st.header("Add Expense")
    with st.form("add_expense"):
        c1, c2, c3 = st.columns(3)
        with c1:
            amount = st.number_input("Amount", min_value=0.0, format="%.2f")
            # Fetch categories for dropdown
            category_options = []
            try:
                cats = api_get("/api/v1/categories").get("categories", [])
                category_options = [c.get("name") for c in cats if c.get("is_active", True)]
            except Exception:
                pass
            category = st.selectbox("Category", options=category_options or ["Food & Dining"], index=0)
            date = st.date_input("Date")
        with c2:
            description = st.text_input("Description", value="")
            merchant = st.text_input("Merchant", value="")
            payment_method = st.selectbox("Payment Method", [
                "credit_card", "debit_card", "cash", "bank_transfer", "digital_wallet", "other"
            ], index=0)
        with c3:
            tags = st.text_input("Tags (comma separated)", value="")
        submitted = st.form_submit_button("Add Expense")
        if submitted:
            payload = {
                "amount": amount,
                "category": category,
                "description": description,
                "date": str(date),
                "merchant": merchant,
                "payment_method": payment_method,
                "tags": [t.strip() for t in tags.split(",") if t.strip()],
            }
            try:
                api_post("/api/v1/expenses", payload)
                st.success("Expense added")
            except Exception as e:
                st.error(f"Failed to add expense: {e}")

    st.header("Recent Expenses (30 days)")
    try:
        data = api_get("/api/v1/expenses?days=30")
        expenses = data.get("expenses", [])
        if expenses:
            df = pd.DataFrame(expenses)
            st.dataframe(df)
        else:
            st.info("No expenses found.")
    except Exception as e:
        st.error(f"Failed to load expenses: {e}")

    st.header("Summary")
    try:
        summary = api_get("/api/v1/expenses/summary?days=30").get("summary")
        if summary:
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Spent", f"${summary['total_spent']:.2f}")
            c2.metric("Avg Daily", f"${summary['avg_daily_spending']:.2f}")
            c3.metric("Transactions", summary["expense_count"])

            cat = pd.DataFrame([
                {"category": k, "amount": v} for k, v in summary["category_breakdown"].items()
            ])
            if not cat.empty:
                chart = alt.Chart(cat).mark_bar().encode(x="category", y="amount")
                st.altair_chart(chart, use_container_width=True)
        else:
            st.info("No summary available.")
    except Exception as e:
        st.error(f"Failed to load summary: {e}")

    st.header("Patterns")
    try:
        patterns = api_get("/api/v1/expenses/patterns?days=90").get("patterns")
        if patterns and patterns.get("weekly_patterns"):
            wp = pd.DataFrame([
                {"weekday": k, "amount": v} for k, v in patterns["weekly_patterns"].items()
            ])
            chart = alt.Chart(wp).mark_bar().encode(x="weekday", y="amount")
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("No pattern data yet.")
    except Exception as e:
        st.error(f"Failed to load patterns: {e}")

elif page == "Portfolio":
    st.header("Portfolio Analysis")
    try:
        payload = api_get("/api/v1/portfolio")
        analysis = payload.get("portfolio_analysis", {})
        st.json(analysis)
    except Exception as e:
        st.error(f"Failed to load portfolio: {e}")

elif page == "Forecast":
    st.header("Financial Forecast")
    try:
        data = api_get("/api/v1/forecast")
        st.json(data.get("forecast", {}))
    except Exception as e:
        st.error(f"Failed to load forecast: {e}")

elif page == "Advice":
    st.header("Quick Advice")
    query = st.text_input("Your question")
    if st.button("Get Advice") and query:
        try:
            base_url, token = get_settings()
            # quick-advice uses query param
            resp = requests.post(f"{base_url}/api/v1/quick-advice", params={"query": query}, headers=auth_headers(token))
            if resp.status_code == 200:
                st.write(resp.json().get("advice"))
            else:
                st.error(resp.text)
        except Exception as e:
            st.error(f"Failed to get advice: {e}")


