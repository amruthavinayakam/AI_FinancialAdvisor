from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
import asyncio

app = FastAPI(
    title="AI Personal Finance Advisor - SIMPLE TEST",
    description="Simple test version to verify the system works",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    """Root endpoint"""
    return {
        "message": "AI Personal Finance Advisor API - SIMPLE TEST",
        "version": "1.0.0",
        "status": "running",
        "note": "This is a simple test version",
        "endpoints": {
            "health": "/health",
            "test_expenses": "/api/v1/test/expenses",
            "test_portfolio": "/api/v1/test/portfolio",
            "test_forecast": "/api/v1/test/forecast",
            "test_advice": "/api/v1/test/advice"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": asyncio.get_event_loop().time(),
        "services": {
            "database": "simulated",
            "ai_services": "simulated",
            "financial_apis": "simulated"
        }
    }

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