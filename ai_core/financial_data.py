import asyncio
import aiohttp
import yfinance as yf
from alpha_vantage.fundamentaldata import FundamentalData
from alpha_vantage.timeseries import TimeSeries
from typing import Dict, List, Any, Optional
import pandas as pd
from .config import ai_config

class FinancialDataCollector:
    """Collects financial data from various APIs and sources"""
    
    def __init__(self):
        self.alpha_vantage_key = ai_config.alpha_vantage_api_key
        self.yahoo_enabled = ai_config.yahoo_finance_enabled
        
        # Initialize Alpha Vantage clients
        if self.alpha_vantage_key:
            self.ts = TimeSeries(key=self.alpha_vantage_key, output_format='pandas')
            self.fd = FundamentalData(key=self.alpha_vantage_key, output_format='pandas')
    
    async def collect_all_data(self, user_id: str) -> Dict[str, Any]:
        """Collect comprehensive financial data for a user"""
        
        # This would typically fetch user's portfolio and preferences from database
        # For now, we'll use sample data
        user_portfolio = await self._get_user_portfolio(user_id)
        
        collected_data = {
            "portfolio": user_portfolio,
            "market_data": {},
            "economic_indicators": {},
            "risk_metrics": {}
        }
        
        # Collect market data for portfolio symbols
        if user_portfolio.get("symbols"):
            collected_data["market_data"] = await self._collect_market_data(
                user_portfolio["symbols"]
            )
        
        # Collect economic indicators
        collected_data["economic_indicators"] = await self._collect_economic_indicators()
        
        # Calculate risk metrics
        collected_data["risk_metrics"] = await self._calculate_risk_metrics(
            collected_data["market_data"]
        )
        
        return collected_data
    
    async def _get_user_portfolio(self, user_id: str) -> Dict[str, Any]:
        """Get user's investment portfolio from database"""
        # TODO: Implement database query
        # For now, return sample portfolio
        return {
            "symbols": ["AAPL", "GOOGL", "MSFT", "TSLA", "SPY"],
            "allocations": {
                "AAPL": 0.25,
                "GOOGL": 0.20,
                "MSFT": 0.20,
                "TSLA": 0.15,
                "SPY": 0.20
            },
            "risk_tolerance": "moderate",
            "investment_horizon": "10+ years",
            "total_value": 100000
        }
    
    async def _collect_market_data(self, symbols: List[str]) -> Dict[str, Any]:
        """Collect real-time market data for portfolio symbols"""
        market_data = {}
        
        # Collect data concurrently
        tasks = []
        for symbol in symbols:
            tasks.append(self._get_symbol_data(symbol))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, symbol in enumerate(symbols):
            if isinstance(results[i], Exception):
                market_data[symbol] = {"error": str(results[i])}
            else:
                market_data[symbol] = results[i]
        
        return market_data
    
    async def _get_symbol_data(self, symbol: str) -> Dict[str, Any]:
        """Get comprehensive data for a single symbol"""
        symbol_data = {}
        
        try:
            # Get data from Yahoo Finance
            if self.yahoo_enabled:
                yahoo_data = await self._get_yahoo_data(symbol)
                symbol_data.update(yahoo_data)
            
            # Get data from Alpha Vantage
            if self.alpha_vantage_key:
                alpha_data = await self._get_alpha_vantage_data(symbol)
                symbol_data.update(alpha_data)
            
        except Exception as e:
            symbol_data["error"] = str(e)
        
        return symbol_data
    
    async def _get_yahoo_data(self, symbol: str) -> Dict[str, Any]:
        """Get data from Yahoo Finance"""
        try:
            ticker = yf.Ticker(symbol)
            
            # Get current info
            info = ticker.info
            
            # Get historical data
            hist = ticker.history(period="1y")
            
            # Calculate additional metrics
            if not hist.empty:
                current_price = hist['Close'].iloc[-1]
                price_change = hist['Close'].iloc[-1] - hist['Close'].iloc[-2]
                price_change_pct = (price_change / hist['Close'].iloc[-2]) * 100
                
                # Calculate volatility (20-day rolling standard deviation)
                volatility = hist['Close'].rolling(window=20).std().iloc[-1]
                
                return {
                    "current_price": float(current_price),
                    "price_change": float(price_change),
                    "price_change_pct": float(price_change_pct),
                    "volume": int(hist['Volume'].iloc[-1]),
                    "market_cap": info.get('marketCap'),
                    "pe_ratio": info.get('trailingPE'),
                    "dividend_yield": info.get('dividendYield'),
                    "volatility": float(volatility),
                    "high_52w": float(hist['High'].max()),
                    "low_52w": float(hist['Low'].min())
                }
            
        except Exception as e:
            return {"error": f"Yahoo Finance error: {str(e)}"}
        
        return {}
    
    async def _get_alpha_vantage_data(self, symbol: str) -> Dict[str, Any]:
        """Get data from Alpha Vantage"""
        try:
            # Get company overview
            overview, _ = self.fd.get_company_overview(symbol)
            
            # Get income statement
            income, _ = self.fd.get_income_statement_annual(symbol)
            
            # Get balance sheet
            balance, _ = self.fd.get_balance_sheet_annual(symbol)
            
            # Get cash flow
            cash_flow, _ = self.fd.get_cash_flow_annual(symbol)
            
            return {
                "company_name": overview.get('Name', ''),
                "sector": overview.get('Sector', ''),
                "industry": overview.get('Industry', ''),
                "revenue": overview.get('RevenueTTM', ''),
                "profit_margin": overview.get('ProfitMargin', ''),
                "return_on_equity": overview.get('ReturnOnEquityTTM', ''),
                "debt_to_equity": overview.get('DebtToEquityRatio', ''),
                "beta": overview.get('Beta', '')
            }
            
        except Exception as e:
            return {"error": f"Alpha Vantage error: {str(e)}"}
    
    async def _collect_economic_indicators(self) -> Dict[str, Any]:
        """Collect key economic indicators"""
        indicators = {}
        
        try:
            if self.alpha_vantage_key:
                # Get economic indicators from Alpha Vantage
                # Note: This would require additional Alpha Vantage API calls
                # For now, we'll return sample data
                indicators = {
                    "inflation_rate": 3.2,
                    "unemployment_rate": 3.8,
                    "gdp_growth": 2.1,
                    "federal_funds_rate": 5.25,
                    "market_sentiment": "neutral"
                }
        except Exception as e:
            indicators["error"] = str(e)
        
        return indicators
    
    async def _calculate_risk_metrics(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate portfolio risk metrics"""
        try:
            # Calculate portfolio volatility
            returns = []
            weights = []
            
            for symbol, data in market_data.items():
                if "volatility" in data and not data.get("error"):
                    returns.append(data["volatility"])
                    # Use equal weights for now, but this should come from user portfolio
                    weights.append(1.0 / len(market_data))
            
            if returns and weights:
                # Calculate weighted average volatility
                portfolio_volatility = sum(r * w for r, w in zip(returns, weights))
                
                # Calculate VaR (Value at Risk) - simplified version
                var_95 = portfolio_volatility * 1.65  # 95% confidence level
                
                return {
                    "portfolio_volatility": portfolio_volatility,
                    "var_95": var_95,
                    "risk_level": self._assess_risk_level(portfolio_volatility),
                    "diversification_score": self._calculate_diversification_score(market_data)
                }
            
        except Exception as e:
            return {"error": f"Risk calculation error: {str(e)}"}
        
        return {}
    
    def _assess_risk_level(self, volatility: float) -> str:
        """Assess portfolio risk level based on volatility"""
        if volatility < 0.15:
            return "low"
        elif volatility < 0.25:
            return "moderate"
        elif volatility < 0.35:
            return "high"
        else:
            return "very_high"
    
    def _calculate_diversification_score(self, market_data: Dict[str, Any]) -> float:
        """Calculate portfolio diversification score (0-100)"""
        try:
            sectors = set()
            total_symbols = len(market_data)
            
            for symbol, data in market_data.items():
                if "sector" in data and not data.get("error"):
                    sectors.add(data["sector"])
            
            # Simple diversification score based on sector coverage
            sector_diversity = len(sectors) / total_symbols if total_symbols > 0 else 0
            return min(100, sector_diversity * 100)
            
        except Exception:
            return 50.0  # Default score 