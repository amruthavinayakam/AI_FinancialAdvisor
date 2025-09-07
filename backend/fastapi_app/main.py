from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import asyncpg
import os
from dotenv import load_dotenv
from typing import Dict, List, Any, Optional
import sys
import asyncio

# Add the AI core module to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'ai_core'))

from ai_core.financial_advisor_graph import FinancialAdvisorGraph
from ai_core.expense_tracker import ExpenseTracker
from ai_core.financial_data import FinancialDataCollector
from ai_core.investment_advisor import InvestmentAdvisor
from ai_core.financial_forecaster import FinancialForecaster

# Load environment variables from .env file
load_dotenv()

app = FastAPI(
    title="AI Personal Finance Advisor",
    description="Comprehensive AI-powered personal finance advisor with expense tracking, investment advice, and financial forecasting",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Read DB config from environment variables or use defaults
DB_USER = os.getenv("POSTGRES_USER", "your_db_user")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "your_db_password")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "your_db_name")

# Initialize AI components
financial_advisor = FinancialAdvisorGraph()
expense_tracker = ExpenseTracker()
financial_collector = FinancialDataCollector()
investment_advisor = InvestmentAdvisor()
forecaster = FinancialForecaster()

@app.on_event("startup")
async def startup():
    """Initialize database connection and AI services"""
    try:
        app.state.db_pool = await asyncpg.create_pool(
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME,
            host=DB_HOST,
            port=DB_PORT
        )
        print("✅ Database connection established")
        
        # Initialize AI services
        print("✅ AI services initialized")
        
    except Exception as e:
        print(f"❌ Startup error: {e}")
        raise e

@app.on_event("shutdown")
async def shutdown():
    """Clean up resources"""
    if hasattr(app.state, 'db_pool'):
        await app.state.db_pool.close()
        print("✅ Database connection closed")

# Dependency for authentication (simplified for demo)
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Get current user from token (simplified implementation)"""
    # TODO: Implement proper JWT token validation
    # For demo purposes, return a sample user ID
    return "user_123"

@app.get("/")
async def read_root():
    """Root endpoint"""
    return {
        "message": "AI Personal Finance Advisor API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "financial_advice": "/api/v1/financial-advice",
            "expenses": "/api/v1/expenses",
            "portfolio": "/api/v1/portfolio",
            "forecast": "/api/v1/forecast",
            "investment_strategy": "/api/v1/investment-strategy"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": asyncio.get_event_loop().time(),
        "services": {
            "database": "connected" if hasattr(app.state, 'db_pool') else "disconnected",
            "ai_services": "initialized"
        }
    }

# Financial Advice Endpoints
@app.post("/api/v1/financial-advice")
async def get_financial_advice(
    query: str,
    user_id: str = Depends(get_current_user)
):
    """Get comprehensive financial advice using AI"""
    try:
        advice = await financial_advisor.get_financial_advice(query, user_id)
        
        if not advice.get("success", False):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=advice.get("error", "Failed to generate financial advice")
            )
        
        return {
            "success": True,
            "advice": advice["advice"],
            "forecast": None,
            "expense_analysis": None,
            "investment_advice": None,
            "timestamp": asyncio.get_event_loop().time()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating financial advice: {str(e)}"
        )

# Expense Tracking Endpoints
@app.get("/api/v1/expenses")
async def get_expenses(
    days: int = 90,
    user_id: str = Depends(get_current_user)
):
    """Get user expenses for the specified number of days"""
    try:
        expenses = await expense_tracker.get_user_expenses(user_id, days)
        
        return {
            "success": True,
            "expenses": expenses,
            "count": len(expenses),
            "period_days": days
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving expenses: {str(e)}"
        )

@app.post("/api/v1/expenses")
async def add_expense(
    expense_data: Dict[str, Any],
    user_id: str = Depends(get_current_user)
):
    """Add a new expense"""
    try:
        result = await expense_tracker.add_expense(user_id, expense_data)
        
        if not result.get("success", False):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Failed to add expense")
            )
        
        return {
            "success": True,
            "message": "Expense added successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding expense: {str(e)}"
        )

@app.get("/api/v1/expenses/summary")
async def get_expense_summary(
    days: int = 30,
    user_id: str = Depends(get_current_user)
):
    """Get expense summary and analytics"""
    try:
        summary = await expense_tracker.get_expense_summary(user_id, days)
        
        if "error" in summary:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=summary["error"]
            )
        
        return {
            "success": True,
            "summary": summary
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating expense summary: {str(e)}"
        )

@app.get("/api/v1/expenses/patterns")
async def get_spending_patterns(
    days: int = 90,
    user_id: str = Depends(get_current_user)
):
    """Get spending patterns and trends"""
    try:
        patterns = await expense_tracker.get_spending_patterns(user_id, days)
        
        if "error" in patterns:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=patterns["error"]
            )
        
        return {
            "success": True,
            "patterns": patterns
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing spending patterns: {str(e)}"
        )

@app.get("/api/v1/expenses/recommendations")
async def get_budget_recommendations(
    user_id: str = Depends(get_current_user)
):
    """Get budget recommendations based on spending patterns"""
    try:
        recommendations = await expense_tracker.get_budget_recommendations(user_id)
        
        if "error" in recommendations:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=recommendations["error"]
            )
        
        return {
            "success": True,
            "recommendations": recommendations
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating budget recommendations: {str(e)}"
        )

# Portfolio and Investment Endpoints
@app.get("/api/v1/portfolio")
async def get_portfolio_analysis(
    user_id: str = Depends(get_current_user)
):
    """Get comprehensive portfolio analysis"""
    try:
        financial_data = await financial_collector.collect_all_data(user_id)
        
        portfolio_analysis = await investment_advisor.analyze_portfolio(financial_data)
        
        if "error" in portfolio_analysis:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=portfolio_analysis["error"]
            )
        
        return {
            "success": True,
            "portfolio_analysis": portfolio_analysis,
            "financial_data": financial_data
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing portfolio: {str(e)}"
        )

@app.post("/api/v1/investment-strategy")
async def get_investment_strategy(
    user_profile: Dict[str, Any],
    user_id: str = Depends(get_current_user)
):
    """Get personalized investment strategy"""
    try:
        strategy = await investment_advisor.get_investment_strategy(user_profile)
        
        if "error" in strategy:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=strategy["error"]
            )
        
        return {
            "success": True,
            "strategy": strategy
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating investment strategy: {str(e)}"
        )

@app.get("/api/v1/market-opportunities")
async def get_market_opportunities(
    user_id: str = Depends(get_current_user)
):
    """Get current market opportunities"""
    try:
        user_profile = {
            "risk_tolerance": "moderate",
            "investment_horizon": "10+ years",
            "age": 35
        }
        
        opportunities = await investment_advisor.get_market_opportunities(user_profile)
        
        if "error" in opportunities:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=opportunities["error"]
            )
        
        return {
            "success": True,
            "opportunities": opportunities
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error identifying market opportunities: {str(e)}"
        )

# Financial Forecasting Endpoints
@app.get("/api/v1/forecast")
async def get_financial_forecast(
    user_id: str = Depends(get_current_user)
):
    """Get comprehensive financial forecast"""
    try:
        financial_data = await financial_collector.collect_all_data(user_id)
        
        expenses = await expense_tracker.get_user_expenses(user_id, 90)
        
        forecast = await forecaster.generate_forecast(financial_data, expenses)
        
        if "error" in forecast:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=forecast["error"]
            )
        
        return {
            "success": True,
            "forecast": forecast
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating financial forecast: {str(e)}"
        )

# Financial Data Endpoints
@app.get("/api/v1/financial-data")
async def get_financial_data(
    user_id: str = Depends(get_current_user)
):
    """Get comprehensive financial data for user"""
    try:
        financial_data = await financial_collector.collect_all_data(user_id)
        
        return {
            "success": True,
            "financial_data": financial_data
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error collecting financial data: {str(e)}"
        )

# Example endpoint using the shared pool
@app.get("/users")
async def get_users():
    """Get users from database (example endpoint)"""
    async with app.state.db_pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM auth_user;")  # Django's default user table
        return [dict(row) for row in rows]

@app.get("/api/v1/test/expenses")
async def test_expenses():
    """Test expense tracking endpoint"""
    return {
        "success": True,
        "expenses": [
            {
                "id": "exp_1",
                "amount": 45.50,
                "category": "Food & Dining",
                "description": "Lunch at restaurant",
                "date": "2025-08-30T12:00:00",
                "merchant": "Local Restaurant"
            },
            {
                "id": "exp_2",
                "amount": 120.00,
                "category": "Transportation",
                "description": "Gas fill-up",
                "date": "2025-08-29T15:30:00",
                "merchant": "Gas Station"
            }
        ],
        "count": 2,
        "period_days": 7
    }

@app.get("/api/v1/test/portfolio")
async def test_portfolio():
    """Test portfolio analysis endpoint"""
    return {
        "success": True,
        "portfolio_analysis": {
            "total_value": 100000,
            "asset_allocation": {
                "stocks": 0.60,
                "bonds": 0.30,
                "cash": 0.10
            },
            "risk_level": "moderate",
            "diversification_score": 75.0,
            "recommendations": [
                "Consider increasing international exposure",
                "Review bond allocation for age-appropriate risk"
            ]
        }
    }

@app.get("/api/v1/test/forecast")
async def test_forecast():
    """Test financial forecast endpoint"""
    return {
        "success": True,
        "forecast": {
            "cash_flow_forecast": {
                "30_days": {
                    "projected_income": 5000,
                    "projected_expenses": 3500,
                    "monthly_cash_flow": 1500
                }
            },
            "net_worth_projection": {
                "365_days": {
                    "projected_net_worth": 110000,
                    "growth_rate": 10.0
                }
            },
            "risk_scenarios": {
                "market_crash": {
                    "scenario": "30% Market Crash",
                    "risk_level": "high",
                    "mitigation_strategies": ["Maintain emergency fund", "Diversify portfolio"]
                }
            }
        }
    }

@app.get("/api/v1/test/advice")
async def test_advice():
    """Test financial advice endpoint"""
    return {
        "success": True,
        "advice": "Here's my AI-powered financial advice: Consider building an emergency fund of 3-6 months of expenses, diversify your investments across different asset classes, and regularly review your budget to identify savings opportunities.",
        "timestamp": asyncio.get_event_loop().time()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 