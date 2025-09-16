from typing import Dict, List, Any, TypedDict
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage
import asyncio
from .config import ai_config
from .financial_data import FinancialDataCollector
from .expense_tracker import ExpenseTracker
from .investment_advisor import InvestmentAdvisor
from .financial_forecaster import FinancialForecaster

class FinancialState(TypedDict):
    """State for the financial advisor workflow"""
    user_query: str
    user_id: str
    financial_data: Dict[str, Any]
    expenses: List[Dict[str, Any]]
    investment_profile: Dict[str, Any]
    recommendations: List[str]
    forecast: Dict[str, Any]
    response: str
    error: str
    expense_analysis: str
    investment_advice: str

class FinancialAdvisorGraph:
    """Main LangGraph workflow for personal finance advice"""
    
    def __init__(self):
        self.openai_llm = ChatOpenAI(
            api_key=ai_config.openai_api_key,
            model=ai_config.openai_model,
            temperature=ai_config.temperature,
            max_tokens=ai_config.max_tokens
        )
        
        self.gemini_llm = ChatGoogleGenerativeAI(
            model=ai_config.google_model,
            google_api_key=ai_config.google_api_key,
            temperature=ai_config.temperature,
            convert_system_message_to_human=True
        )
        
        self.financial_collector = FinancialDataCollector()
        self.expense_tracker = ExpenseTracker()
        self.investment_advisor = InvestmentAdvisor()
        self.forecaster = FinancialForecaster()
        
        # Build the workflow graph
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow"""
        
        workflow = StateGraph(FinancialState)
        
        # Add nodes
        workflow.add_node("collect_financial_data", self._collect_financial_data)
        workflow.add_node("analyze_expenses", self._analyze_expenses)
        workflow.add_node("generate_investment_advice", self._generate_investment_advice)
        workflow.add_node("forecast_financial_health", self._forecast_financial_health)
        workflow.add_node("synthesize_advice", self._synthesize_advice)
        
        # Define the flow
        workflow.set_entry_point("collect_financial_data")
        workflow.add_edge("collect_financial_data", "analyze_expenses")
        workflow.add_edge("analyze_expenses", "generate_investment_advice")
        workflow.add_edge("generate_investment_advice", "forecast_financial_health")
        workflow.add_edge("forecast_financial_health", "synthesize_advice")
        workflow.add_edge("synthesize_advice", END)
        
        return workflow.compile()
    
    async def _collect_financial_data(self, state: FinancialState) -> FinancialState:
        """Collect financial data from various sources"""
        try:
            user_id = state["user_id"]
            
            # Collect financial data
            financial_data = await self.financial_collector.collect_all_data(user_id)
            
            # Collect expenses
            expenses = await self.expense_tracker.get_user_expenses(user_id)
            
            state["financial_data"] = financial_data
            state["expenses"] = expenses
            
        except Exception as e:
            state["error"] = f"Error collecting financial data: {str(e)}"
        
        return state
    
    async def _analyze_expenses(self, state: FinancialState) -> FinancialState:
        """Analyze user expenses using AI"""
        try:
            expenses = state["expenses"]
            
            # Summarize expenses to reduce token usage
            expense_summary = self._summarize_expenses(expenses)
            
            # Use OpenAI for expense analysis (more reliable)
            expense_analysis_prompt = f"""
            Analyze the following expense summary and provide insights:
            {expense_summary}
            
            Provide:
            1. Spending patterns
            2. Areas for potential savings
            3. Budget recommendations
            """
            
            response = await self.openai_llm.ainvoke([
                SystemMessage(content="You are a financial expert analyzing personal expenses."),
                HumanMessage(content=expense_analysis_prompt)
            ])
            
            state["expense_analysis"] = response.content
            
        except Exception as e:
            state["error"] = f"Error analyzing expenses: {str(e)}"
        
        return state
    
    def _summarize_expenses(self, expenses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Summarize expenses to reduce token usage"""
        if not expenses:
            return {"total_expenses": 0, "categories": {}, "count": 0}
        
        # Calculate totals by category
        category_totals = {}
        total_amount = 0
        
        for expense in expenses[:50]:  # Limit to first 50 expenses
            category = expense.get('category', 'Other')
            amount = expense.get('amount', 0)
            
            if category not in category_totals:
                category_totals[category] = 0
            category_totals[category] += amount
            total_amount += amount
        
        # Get top 10 categories
        top_categories = dict(sorted(category_totals.items(), key=lambda x: x[1], reverse=True)[:10])
        
        return {
            "total_expenses": total_amount,
            "expense_count": len(expenses),
            "top_categories": top_categories,
            "average_expense": total_amount / len(expenses) if expenses else 0
        }
    
    async def _generate_investment_advice(self, state: FinancialState) -> FinancialState:
        """Generate investment advice using AI"""
        try:
            financial_data = state["financial_data"]
            user_query = state["user_query"]
            
            # Summarize financial data to reduce token usage
            portfolio_summary = self._summarize_portfolio(financial_data)
            
            # Use GPT-4 for investment advice
            investment_prompt = f"""
            Based on the user's financial data and query, provide personalized investment advice:
            
            User Query: {user_query}
            Portfolio Summary: {portfolio_summary}
            
            Provide:
            1. Risk assessment
            2. Investment strategy recommendations
            3. Portfolio allocation suggestions
            4. Market timing considerations
            """
            
            response = await self.openai_llm.ainvoke([
                SystemMessage(content="You are a certified financial advisor providing investment guidance."),
                HumanMessage(content=investment_prompt)
            ])
            
            state["investment_advice"] = response.content
            
        except Exception as e:
            state["error"] = f"Error generating investment advice: {str(e)}"
        
        return state
    
    def _summarize_portfolio(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize portfolio data to reduce token usage"""
        portfolio = financial_data.get("portfolio", {})
        market_data = financial_data.get("market_data", {})
        
        # Extract key portfolio info
        portfolio_summary = {
            "total_value": portfolio.get("total_value", 0),
            "risk_tolerance": portfolio.get("risk_tolerance", "moderate"),
            "investment_horizon": portfolio.get("investment_horizon", "10+ years"),
            "symbols": portfolio.get("symbols", []),
            "allocations": portfolio.get("allocations", {}),
            "market_performance": {}
        }
        
        # Summarize market data for each symbol
        for symbol, data in market_data.items():
            if not data.get("error"):
                portfolio_summary["market_performance"][symbol] = {
                    "current_price": data.get("current_price", 0),
                    "price_change_pct": data.get("price_change_pct", 0),
                    "sector": data.get("sector", "Unknown")
                }
        
        return portfolio_summary
    
    async def _forecast_financial_health(self, state: FinancialState) -> FinancialState:
        """Forecast financial health using AI models"""
        try:
            financial_data = state["financial_data"]
            expenses = state["expenses"]
            
            # Generate financial forecast
            forecast = await self.forecaster.generate_forecast(
                financial_data, expenses
            )
            
            state["forecast"] = forecast
            
        except Exception as e:
            state["error"] = f"Error forecasting financial health: {str(e)}"
        
        return state
    
    async def _synthesize_advice(self, state: FinancialState) -> FinancialState:
        """Synthesize all advice into a comprehensive response"""
        try:
            # Combine all insights using GPT-4
            synthesis_prompt = f"""
            Synthesize the following financial advice into a comprehensive, actionable response:
            
            Expense Analysis: {state.get('expense_analysis', 'N/A')}
            Investment Advice: {state.get('investment_advice', 'N/A')}
            Financial Forecast: {state.get('forecast', 'N/A')}
            
            Provide a clear, structured response with:
            1. Executive Summary
            2. Key Recommendations
            3. Action Items
            4. Risk Warnings
            5. Next Steps
            """
            
            response = await self.openai_llm.ainvoke([
                SystemMessage(content="You are a senior financial advisor creating comprehensive financial plans."),
                HumanMessage(content=synthesis_prompt)
            ])
            
            state["response"] = response.content
            
        except Exception as e:
            state["error"] = f"Error synthesizing advice: {str(e)}"
        
        return state
    
    async def get_financial_advice(self, user_query: str, user_id: str) -> Dict[str, Any]:
        """Main method to get financial advice"""
        
        initial_state = FinancialState(
            user_query=user_query,
            user_id=user_id,
            financial_data={},
            expenses=[],
            investment_profile={},
            recommendations=[],
            forecast={},
            response="",
            error="",
            expense_analysis="",
            investment_advice=""
        )
        
        try:
            # Run the workflow
            final_state = await self.workflow.ainvoke(initial_state)
            
            if final_state.get("error"):
                return {
                    "success": False,
                    "error": final_state["error"],
                    "advice": None
                }
            
            return {
                "success": True,
                "advice": final_state["response"],
                "forecast": final_state["forecast"],
                "expense_analysis": final_state.get("expense_analysis"),
                "investment_advice": final_state.get("investment_advice")
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Workflow execution failed: {str(e)}",
                "advice": None
            } 