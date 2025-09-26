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


def inject_global_css() -> None:
    """Inject lightweight global styles to modernize look without external deps."""
    st.markdown(
        """
        <style>
        /* Base tweaks */
        .block-container { padding-top: 2rem; padding-bottom: 2rem; }
        header[data-testid="stHeader"] { background: linear-gradient(90deg, #0ea5e9, #22c55e); }
        /* Sidebar */
        section[data-testid="stSidebar"] > div { padding-top: 1rem; }
        /* Metrics */
        div[data-testid="stMetric"] { background: #0b132414; border-radius: 12px; padding: 12px; }
        div[data-testid="stMetric"] label { color: #475569; }
        /* Subheaders spacing */
        h3, h2 { margin-top: 0.75rem; }
        /* Buttons */
        .stButton>button { border-radius: 10px; padding: 0.5rem 0.9rem; }
        /* Pills */
        .pill { display:inline-block; padding:6px 10px; border-radius:20px; background:#f1f5f9; margin:4px; font-size:0.9rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def configure_charts() -> None:
    """Register and enable a subtle Altair theme for consistent charts."""
    def _theme():
        return {
            "config": {
                "view": {"continuousWidth": 400, "continuousHeight": 300},
                "range": {"category": {"scheme": "tealblues"}},
                "axis": {"labelColor": "#334155", "titleColor": "#0f172a"},
                "legend": {"labelColor": "#334155", "titleColor": "#0f172a"},
            }
        }

    alt.themes.register("advisor_theme", _theme)
    alt.themes.enable("advisor_theme")


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
inject_global_css()
configure_charts()

st.sidebar.title("Settings")
api_url, api_token = get_settings()
st.session_state.api_url = st.sidebar.text_input("API URL", api_url, help="FastAPI base URL")
st.session_state.api_token = st.sidebar.text_input("Bearer Token", api_token, type="password", help="JWT or dev token")

page = st.sidebar.radio("Navigation", ["Expenses", "Portfolio", "Forecast", "Advice"]) 

st.title("AI Personal Finance Advisor ✨")
st.caption("Smarter insights for your money, with clean visuals.")

if page == "Expenses":
    tabs = st.tabs(["Add", "Recent", "Summary", "Patterns"])
    with tabs[0]:
        st.subheader("Add Expense")
        with st.form("add_expense"):
            c1, c2, c3 = st.columns(3)
            with c1:
                amount = st.number_input("Amount", min_value=0.0, format="%.2f")
                # Fetch categories for dropdown
                category_options = []
                try:
                    with st.spinner("Loading categories..."):
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
                    with st.spinner("Saving expense..."):
                        api_post("/api/v1/expenses", payload)
                    st.success("Expense added")
                except Exception as e:
                    st.error(f"Failed to add expense: {e}")

    with tabs[1]:
        st.subheader("Recent Expenses (30 days)")
        try:
            with st.spinner("Loading expenses..."):
                data = api_get("/api/v1/expenses?days=30")
            expenses = data.get("expenses", [])
            if expenses:
                df = pd.DataFrame(expenses)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No expenses found.")
        except Exception as e:
            st.error(f"Failed to load expenses: {e}")

    with tabs[2]:
        st.subheader("Summary")
        try:
            with st.spinner("Computing summary..."):
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
                    chart = alt.Chart(cat).mark_bar().encode(
                        x=alt.X("category", title="Category"),
                        y=alt.Y("amount", title="Amount"),
                        tooltip=["category", "amount"]
                    )
                    st.altair_chart(chart, use_container_width=True)
            else:
                st.info("No summary available.")
        except Exception as e:
            st.error(f"Failed to load summary: {e}")

    with tabs[3]:
        st.subheader("Patterns")
        try:
            with st.spinner("Finding patterns..."):
                patterns = api_get("/api/v1/expenses/patterns?days=90").get("patterns")
            if patterns and patterns.get("weekly_patterns"):
                wp = pd.DataFrame([
                    {"weekday": k, "amount": v} for k, v in patterns["weekly_patterns"].items()
                ])
                chart = alt.Chart(wp).mark_bar().encode(
                    x=alt.X("weekday", title="Weekday"),
                    y=alt.Y("amount", title="Amount"),
                    tooltip=["weekday", "amount"]
                )
                st.altair_chart(chart, use_container_width=True)
            else:
                st.info("No pattern data yet.")
        except Exception as e:
            st.error(f"Failed to load patterns: {e}")

elif page == "Portfolio":
    st.header("Portfolio Analysis")
    try:
        with st.spinner("Loading portfolio analysis..."):
            payload = api_get("/api/v1/portfolio")
        analysis = payload.get("portfolio_analysis", {})

        if not analysis:
            st.info("No portfolio analysis available.")
        else:
            t_overview, t_alloc, t_sector, t_perf, t_risk, t_recs, t_raw = st.tabs([
                "Overview", "Allocation", "Sectors", "Performance", "Risk", "Recommendations", "Raw"
            ])

            with t_overview:
                c1, c2, c3 = st.columns(3)
                total_value = analysis.get("total_value")
                overall_health = analysis.get("overall_health_score")
                risk_level = (analysis.get("risk_analysis") or {}).get("risk_level")
                if total_value is not None:
                    c1.metric("Total Value", f"${total_value:,.0f}")
                if overall_health is not None:
                    c2.metric("Overall Health", f"{overall_health}")
                if risk_level:
                    c3.metric("Risk Level", risk_level.title())

            with t_alloc:
                allocation = analysis.get("asset_allocation") or {}
                if allocation:
                    alloc_df = pd.DataFrame([
                        {"asset": k.replace("_", " ").title(), "weight": float(v)} for k, v in allocation.items()
                    ])
                    chart = alt.Chart(alloc_df).mark_bar().encode(
                        x=alt.X("asset", sort="-y", title="Asset Class"),
                        y=alt.Y("weight", axis=alt.Axis(format='%'), title="Portfolio Weight"),
                        tooltip=["asset", alt.Tooltip("weight", format=".0%")]
                    )
                    st.altair_chart(chart, use_container_width=True)
                else:
                    st.info("No allocation data.")

            with t_sector:
                sectors = analysis.get("sector_analysis") or {}
                if sectors:
                    sector_df = pd.DataFrame([
                        {"sector": k.replace("_", " ").title(), "weight": float(v)} for k, v in sectors.items()
                    ])
                    chart = alt.Chart(sector_df).mark_bar().encode(
                        x=alt.X("sector", sort="-y", title="Sector"),
                        y=alt.Y("weight", axis=alt.Axis(format='%'), title="Portfolio Weight"),
                        tooltip=["sector", alt.Tooltip("weight", format=".0%")]
                    )
                    st.altair_chart(chart, use_container_width=True)
                else:
                    st.info("No sector data.")

            with t_perf:
                perf = analysis.get("performance_analysis") or {}
                p1, p2, p3 = st.columns(3)
                if perf.get("total_return_1y") is not None:
                    p1.metric("1Y Return", f"{perf['total_return_1y']*100:.2f}%")
                if perf.get("total_return_3y") is not None:
                    p2.metric("3Y Return", f"{perf['total_return_3y']*100:.2f}%")
                if perf.get("total_return_5y") is not None:
                    p3.metric("5Y Return", f"{perf['total_return_5y']*100:.2f}%")
                q1, q2, q3 = st.columns(3)
                if perf.get("volatility") is not None:
                    q1.metric("Volatility", f"{perf['volatility']*100:.2f}%")
                if perf.get("sharpe_ratio") is not None:
                    q2.metric("Sharpe Ratio", f"{perf['sharpe_ratio']:.2f}")
                if perf.get("max_drawdown") is not None:
                    q3.metric("Max Drawdown", f"{perf['max_drawdown']*100:.2f}%")

            with t_risk:
                risk = analysis.get("risk_analysis") or {}
                r1, r2, r3 = st.columns(3)
                if risk.get("concentration_risk") is not None:
                    r1.metric("Concentration Risk", f"{risk['concentration_risk']*100:.2f}%")
                if risk.get("diversification_score") is not None:
                    r2.metric("Diversification Score", f"{risk['diversification_score']}")
                if risk.get("num_holdings") is not None:
                    r3.metric("Number of Holdings", f"{risk['num_holdings']}")

            with t_recs:
                recs = analysis.get("rebalancing_recommendations") or []
                if recs:
                    for rec in recs:
                        st.write(f"- {rec}")
                else:
                    st.info("No rebalancing actions recommended.")

            with t_raw:
                st.json(analysis)
    except Exception as e:
        st.error(f"Failed to load portfolio: {e}")

elif page == "Forecast":
    st.header("Financial Forecast")
    try:
        with st.spinner("Generating forecast..."):
            data = api_get("/api/v1/forecast")
        forecast = data.get("forecast", {})

        if not forecast:
            st.info("No forecast available.")
        else:
            cash_flow = forecast.get("cash_flow_forecast") or {}
            net_worth = forecast.get("net_worth_projection") or {}
            risks = forecast.get("risk_scenarios") or {}

            t_overview, t_cash, t_networth, t_risk, t_raw = st.tabs([
                "Overview", "Cash Flow", "Net Worth", "Risk", "Raw"
            ])

            with t_cash:
                st.subheader("Cash Flow Forecast")
                horizon_key = None
                if isinstance(cash_flow, dict) and cash_flow:
                    horizon_key = "30_days" if "30_days" in cash_flow else list(cash_flow.keys())[0]
                if horizon_key:
                    cf = cash_flow.get(horizon_key) or {}
                    c1, c2, c3 = st.columns(3)
                    if cf.get("projected_income") is not None:
                        c1.metric("Projected Income", f"${cf['projected_income']:,.0f}")
                    if cf.get("projected_expenses") is not None:
                        c2.metric("Projected Expenses", f"${cf['projected_expenses']:,.0f}")
                    if cf.get("monthly_cash_flow") is not None:
                        c3.metric("Monthly Cash Flow", f"${cf['monthly_cash_flow']:,.0f}")
                else:
                    st.info("No cash flow details available.")

            with t_networth:
                st.subheader("Net Worth Projection")
                nw_key = None
                if isinstance(net_worth, dict) and net_worth:
                    nw_key = "365_days" if "365_days" in net_worth else list(net_worth.keys())[0]
                if nw_key:
                    nw = net_worth.get(nw_key) or {}
                    d1, d2 = st.columns(2)
                    if nw.get("projected_net_worth") is not None:
                        d1.metric("Projected Net Worth", f"${nw['projected_net_worth']:,.0f}")
                    if nw.get("growth_rate") is not None:
                        d2.metric("Growth Rate", f"{float(nw['growth_rate']):.2f}%")
                else:
                    st.info("No net worth projection available.")

            with t_risk:
                st.subheader("Risk Scenarios")
                if risks:
                    for key, scenario in risks.items():
                        name = scenario.get("scenario") or str(key).replace("_", " ").title()
                        risk_level = scenario.get("risk_level", "unknown").title()
                        st.markdown(f"**{name}** — Risk: {risk_level}")
                        strategies = scenario.get("mitigation_strategies") or []
                        if strategies:
                            for s in strategies:
                                st.write(f"- {s}")
                else:
                    st.info("No risk scenarios provided.")

            with t_overview:
                # Simple recap using available keys
                c1, c2 = st.columns(2)
                # Cash flow summary if available
                if isinstance(cash_flow, dict) and cash_flow:
                    hk = "30_days" if "30_days" in cash_flow else list(cash_flow.keys())[0]
                    cf = cash_flow.get(hk) or {}
                    if cf.get("monthly_cash_flow") is not None:
                        c1.metric("Next Month Cash Flow", f"${cf['monthly_cash_flow']:,.0f}")
                # Net worth summary if available
                if isinstance(net_worth, dict) and net_worth:
                    nk = "365_days" if "365_days" in net_worth else list(net_worth.keys())[0]
                    nw = net_worth.get(nk) or {}
                    if nw.get("projected_net_worth") is not None:
                        c2.metric("1Y Net Worth", f"${nw['projected_net_worth']:,.0f}")

            with t_raw:
                st.json(forecast)
    except Exception as e:
        st.error(f"Failed to load forecast: {e}")

elif page == "Advice":
    st.header("Quick Advice")
    suggestions = [
        "How do I save more?",
        "How can I reduce debt?",
        "Am I diversified enough?",
        "How much emergency fund?",
    ]
    if "advice_query" not in st.session_state:
        st.session_state.advice_query = ""
    if "advice_should_submit" not in st.session_state:
        st.session_state.advice_should_submit = False

    def _select_suggestion(q: str):
        st.session_state.advice_query = q
        st.session_state.advice_should_submit = True

    st.write("Try a quick question:")
    cols = st.columns(4)
    for i, s in enumerate(suggestions):
        cols[i].button(s, key=f"suggestion_{i}", on_click=_select_suggestion, args=(s,))

    query = st.text_input("Your question", key="advice_query")
    submit_clicked = st.button("Get Advice")
    should_submit = submit_clicked or st.session_state.advice_should_submit
    if should_submit and (st.session_state.advice_query or "").strip():
        try:
            base_url, token = get_settings()
            with st.spinner("Thinking..."):
                resp = requests.post(
                    f"{base_url}/api/v1/financial-advice",
                    params={"query": st.session_state.advice_query},
                    headers=auth_headers(token)
                )
            st.session_state.advice_should_submit = False
            if resp.status_code == 200:
                data = resp.json()
                st.success("Here's my take:")
                st.write(data.get("advice"))
            else:
                st.error(resp.text)
        except Exception as e:
            st.session_state.advice_should_submit = False
            st.error(f"Failed to get advice: {e}")


