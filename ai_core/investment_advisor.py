from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import asyncio

class InvestmentAdvisor:
    """Provides investment advice and portfolio recommendations"""
    
    def __init__(self):
        # Investment strategy templates
        self.strategies = {
            "conservative": {
                "bonds": 0.60,
                "stocks": 0.30,
                "cash": 0.10,
                "description": "Low risk, stable returns, suitable for retirees or risk-averse investors"
            },
            "moderate": {
                "bonds": 0.40,
                "stocks": 0.50,
                "cash": 0.10,
                "description": "Balanced approach, moderate risk and return potential"
            },
            "aggressive": {
                "bonds": 0.20,
                "stocks": 0.70,
                "cash": 0.10,
                "description": "Higher risk, higher return potential, suitable for long-term investors"
            },
            "growth": {
                "bonds": 0.10,
                "stocks": 0.80,
                "cash": 0.10,
                "description": "Maximum growth potential, highest risk, for young investors with long time horizon"
            }
        }
        
        # Asset class recommendations
        self.asset_classes = {
            "stocks": {
                "large_cap": ["SPY", "VOO", "IVV"],  # S&P 500 ETFs
                "mid_cap": ["IJH", "VO"],            # Mid-cap ETFs
                "small_cap": ["IJR", "VB"],          # Small-cap ETFs
                "international": ["EFA", "VEA"],     # International developed
                "emerging_markets": ["EEM", "VWO"],  # Emerging markets
                "technology": ["XLK", "VGT"],        # Technology sector
                "healthcare": ["XLV", "VHT"],        # Healthcare sector
                "financial": ["XLF", "VFH"]          # Financial sector
            },
            "bonds": {
                "government": ["BND", "AGG"],        # Government bonds
                "corporate": ["LQD", "VCIT"],        # Corporate bonds
                "municipal": ["MUB", "VTEB"],        # Municipal bonds
                "international": ["BNDX", "IGOV"]    # International bonds
            },
            "alternatives": {
                "real_estate": ["VNQ", "IYR"],       # REITs
                "commodities": ["GLD", "SLV"],       # Gold/Silver
                "infrastructure": ["IFRA", "UTF"]    # Infrastructure
            }
        }
    
    async def get_investment_strategy(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Generate personalized investment strategy based on user profile"""
        try:
            risk_tolerance = user_profile.get("risk_tolerance", "moderate")
            age = user_profile.get("age", 35)
            investment_horizon = user_profile.get("investment_horizon", "10+ years")
            financial_goals = user_profile.get("financial_goals", [])
            current_portfolio = user_profile.get("current_portfolio", {})
            
            # Determine base strategy
            base_strategy = self._determine_base_strategy(risk_tolerance, age, investment_horizon)
            
            # Customize strategy based on goals
            customized_strategy = self._customize_for_goals(base_strategy, financial_goals)
            
            # Generate specific recommendations
            recommendations = await self._generate_recommendations(
                customized_strategy, user_profile, current_portfolio
            )
            
            # Calculate expected returns and risk
            risk_metrics = self._calculate_strategy_risk_metrics(customized_strategy)
            
            return {
                "strategy_name": base_strategy["name"],
                "asset_allocation": customized_strategy["allocation"],
                "description": customized_strategy["description"],
                "recommendations": recommendations,
                "risk_metrics": risk_metrics,
                "rebalancing_schedule": self._get_rebalancing_schedule(risk_tolerance),
                "monitoring_frequency": self._get_monitoring_frequency(risk_tolerance)
            }
            
        except Exception as e:
            return {"error": f"Error generating investment strategy: {str(e)}"}
    
    async def analyze_portfolio(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze current portfolio and provide insights"""
        try:
            holdings = portfolio_data.get("holdings", {})
            
            if not holdings:
                return {"error": "No portfolio holdings found"}
            
            # Calculate portfolio metrics
            total_value = sum(holding.get("value", 0) for holding in holdings.values())
            
            # Asset allocation analysis
            asset_allocation = self._calculate_asset_allocation(holdings)
            
            # Sector analysis
            sector_analysis = self._analyze_sector_exposure(holdings)
            
            # Risk analysis
            risk_analysis = self._analyze_portfolio_risk(holdings)
            
            # Performance analysis
            performance_analysis = await self._analyze_portfolio_performance(holdings)
            
            # Rebalancing recommendations
            rebalancing_recommendations = self._get_rebalancing_recommendations(
                asset_allocation, portfolio_data.get("target_allocation", {})
            )
            
            return {
                "total_value": total_value,
                "asset_allocation": asset_allocation,
                "sector_analysis": sector_analysis,
                "risk_analysis": risk_analysis,
                "performance_analysis": performance_analysis,
                "rebalancing_recommendations": rebalancing_recommendations,
                "overall_health_score": self._calculate_portfolio_health_score(
                    asset_allocation, risk_analysis, performance_analysis
                )
            }
            
        except Exception as e:
            return {"error": f"Error analyzing portfolio: {str(e)}"}
    
    async def get_market_opportunities(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Identify current market opportunities based on user profile"""
        try:
            risk_tolerance = user_profile.get("risk_tolerance", "moderate")
            investment_horizon = user_profile.get("investment_horizon", "10+ years")
            
            # Get market analysis (this would typically come from external data)
            market_analysis = await self._get_market_analysis()
            
            # Filter opportunities based on user profile
            opportunities = self._filter_opportunities_by_profile(
                market_analysis, risk_tolerance, investment_horizon
            )
            
            # Rank opportunities by potential return and risk
            ranked_opportunities = self._rank_opportunities(opportunities)
            
            return {
                "market_analysis": market_analysis,
                "opportunities": ranked_opportunities,
                "recommended_actions": self._generate_action_recommendations(ranked_opportunities)
            }
            
        except Exception as e:
            return {"error": f"Error identifying market opportunities: {str(e)}"}
    
    def _determine_base_strategy(self, risk_tolerance: str, age: int, horizon: str) -> Dict[str, Any]:
        """Determine base investment strategy"""
        
        # Adjust strategy based on age and time horizon
        if age < 30 and "long" in horizon.lower():
            base_strategy = "growth"
        elif age > 60 or "short" in horizon.lower():
            base_strategy = "conservative"
        else:
            base_strategy = risk_tolerance
        
        strategy = self.strategies.get(base_strategy, self.strategies["moderate"])
        
        return {
            "name": base_strategy,
            "allocation": strategy.copy(),
            "description": strategy["description"]
        }
    
    def _customize_for_goals(self, base_strategy: Dict[str, Any], goals: List[str]) -> Dict[str, Any]:
        """Customize strategy based on financial goals"""
        allocation = base_strategy["allocation"].copy()
        
        # Adjust allocation based on goals
        if "retirement" in goals:
            # Increase bond allocation for stability
            allocation["bonds"] = min(0.8, allocation["bonds"] * 1.2)
            allocation["stocks"] = max(0.1, allocation["stocks"] * 0.8)
        
        if "education" in goals:
            # More conservative for education funding
            allocation["bonds"] = min(0.7, allocation["bonds"] * 1.1)
            allocation["cash"] = min(0.2, allocation["cash"] * 1.5)
        
        if "emergency_fund" in goals:
            # Increase cash allocation
            allocation["cash"] = min(0.25, allocation["cash"] * 1.5)
            allocation["stocks"] = max(0.05, allocation["stocks"] * 0.9)
        
        # Normalize to ensure allocations sum to 1.0
        total = sum(allocation.values())
        for key in allocation:
            allocation[key] = allocation[key] / total
        
        return {
            "allocation": allocation,
            "description": base_strategy["description"]
        }
    
    async def _generate_recommendations(self, strategy: Dict[str, Any], 
                                      user_profile: Dict[str, Any], 
                                      current_portfolio: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate specific investment recommendations"""
        recommendations = []
        allocation = strategy["allocation"]
        
        # Generate recommendations for each asset class
        for asset_class, target_percentage in allocation.items():
            if target_percentage > 0.05:  # Only recommend if allocation > 5%
                specific_recommendations = self._get_asset_class_recommendations(
                    asset_class, target_percentage, user_profile
                )
                recommendations.extend(specific_recommendations)
        
        # Add portfolio-specific recommendations
        if current_portfolio:
            portfolio_recommendations = self._get_portfolio_specific_recommendations(
                current_portfolio, allocation
            )
            recommendations.extend(portfolio_recommendations)
        
        return recommendations
    
    def _get_asset_class_recommendations(self, asset_class: str, target_percentage: float, 
                                       user_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get specific recommendations for an asset class"""
        recommendations = []
        
        if asset_class == "stocks":
            # Recommend stock ETFs based on user profile
            if user_profile.get("age", 35) < 40:
                # Younger investors can take more risk
                recommendations.append({
                    "type": "stock_etf",
                    "symbol": "VTI",  # Total US Stock Market
                    "allocation": target_percentage * 0.6,
                    "reason": "Broad market exposure with growth potential"
                })
                recommendations.append({
                    "type": "international_stock",
                    "symbol": "VXUS",  # Total International Stock
                    "allocation": target_percentage * 0.4,
                    "reason": "Geographic diversification"
                })
            else:
                # More conservative approach for older investors
                recommendations.append({
                    "type": "stock_etf",
                    "symbol": "SPY",  # S&P 500
                    "allocation": target_percentage * 0.8,
                    "reason": "Large-cap stability with dividend income"
                })
                recommendations.append({
                    "type": "dividend_stock",
                    "symbol": "VYM",  # High Dividend Yield
                    "allocation": target_percentage * 0.2,
                    "reason": "Income generation"
                })
        
        elif asset_class == "bonds":
            recommendations.append({
                "type": "bond_etf",
                "symbol": "BND",  # Total Bond Market
                "allocation": target_percentage * 0.7,
                "reason": "Core bond exposure for stability"
            })
            recommendations.append({
                "type": "treasury_bond",
                "symbol": "TLT",  # Long-term Treasury
                "allocation": target_percentage * 0.3,
                "reason": "Government-backed safety"
            })
        
        elif asset_class == "cash":
            recommendations.append({
                "type": "money_market",
                "symbol": "SPRXX",  # Fidelity Money Market
                "allocation": target_percentage,
                "reason": "Liquidity and safety"
            })
        
        return recommendations
    
    def _get_portfolio_specific_recommendations(self, current_portfolio: Dict[str, Any], 
                                             target_allocation: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get recommendations based on current portfolio analysis"""
        recommendations = []
        
        # Analyze current vs target allocation
        current_allocation = self._calculate_asset_allocation(current_portfolio.get("holdings", {}))
        
        for asset_class, target_pct in target_allocation.items():
            current_pct = current_allocation.get(asset_class, 0)
            difference = target_pct - current_pct
            
            if abs(difference) > 0.05:  # If difference > 5%
                if difference > 0:
                    recommendations.append({
                        "type": "increase_allocation",
                        "asset_class": asset_class,
                        "current": current_pct,
                        "target": target_pct,
                        "action": f"Increase {asset_class} allocation from {current_pct:.1%} to {target_pct:.1%}"
                    })
                else:
                    recommendations.append({
                        "type": "decrease_allocation",
                        "asset_class": asset_class,
                        "current": current_pct,
                        "target": target_pct,
                        "action": f"Decrease {asset_class} allocation from {current_pct:.1%} to {target_pct:.1%}"
                    })
        
        return recommendations
    
    def _calculate_asset_allocation(self, holdings: Dict[str, Any]) -> Dict[str, float]:
        """Calculate current asset allocation"""
        total_value = sum(holding.get("value", 0) for holding in holdings.values())
        
        if total_value == 0:
            return {}
        
        allocation = {}
        for symbol, holding in holdings.items():
            asset_class = self._classify_asset(symbol, holding)
            current_value = holding.get("value", 0)
            
            if asset_class not in allocation:
                allocation[asset_class] = 0
            
            allocation[asset_class] += current_value / total_value
        
        return allocation
    
    def _classify_asset(self, symbol: str, holding: Dict[str, Any]) -> str:
        """Classify an asset into broad categories"""
        symbol_upper = symbol.upper()
        
        # Bond ETFs
        if any(bond in symbol_upper for bond in ["BND", "AGG", "LQD", "MUB", "TLT", "SHY"]):
            return "bonds"
        
        # Cash equivalents
        if any(cash in symbol_upper for cash in ["SPRXX", "SPAXX", "FDRXX"]):
            return "cash"
        
        # Default to stocks
        return "stocks"
    
    def _analyze_sector_exposure(self, holdings: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze sector exposure of portfolio"""
        # This would typically use sector data from financial APIs
        # For now, return sample analysis
        return {
            "technology": 0.25,
            "healthcare": 0.20,
            "financial": 0.15,
            "consumer_discretionary": 0.15,
            "industrial": 0.10,
            "other": 0.15
        }
    
    def _analyze_portfolio_risk(self, holdings: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze portfolio risk metrics"""
        # Calculate basic risk metrics
        total_value = sum(holding.get("value", 0) for holding in holdings.values())
        
        if total_value == 0:
            return {"error": "No portfolio value"}
        
        # Calculate concentration risk
        largest_holding = max((holding.get("value", 0) for holding in holdings.values()), default=0)
        concentration_risk = largest_holding / total_value if total_value > 0 else 0
        
        # Calculate diversification score
        num_holdings = len(holdings)
        diversification_score = min(100, (num_holdings / 20) * 100)  # Max score at 20+ holdings
        
        return {
            "concentration_risk": concentration_risk,
            "diversification_score": diversification_score,
            "num_holdings": num_holdings,
            "risk_level": self._assess_portfolio_risk_level(concentration_risk, diversification_score)
        }
    
    def _assess_portfolio_risk_level(self, concentration_risk: float, diversification_score: float) -> str:
        """Assess overall portfolio risk level"""
        if concentration_risk > 0.25 or diversification_score < 30:
            return "high"
        elif concentration_risk > 0.15 or diversification_score < 60:
            return "moderate"
        else:
            return "low"
    
    async def _analyze_portfolio_performance(self, holdings: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze portfolio performance metrics"""
        # This would typically calculate actual returns from historical data
        # For now, return sample metrics
        return {
            "total_return_1y": 0.08,
            "total_return_3y": 0.12,
            "total_return_5y": 0.15,
            "volatility": 0.18,
            "sharpe_ratio": 0.45,
            "max_drawdown": -0.12
        }
    
    def _get_rebalancing_recommendations(self, current_allocation: Dict[str, float], 
                                       target_allocation: Dict[str, float]) -> List[Dict[str, Any]]:
        """Get rebalancing recommendations"""
        recommendations = []
        
        for asset_class, target_pct in target_allocation.items():
            current_pct = current_allocation.get(asset_class, 0)
            difference = target_pct - current_pct
            
            if abs(difference) > 0.05:  # If difference > 5%
                recommendations.append({
                    "asset_class": asset_class,
                    "current": current_pct,
                    "target": target_pct,
                    "difference": difference,
                    "action": "buy" if difference > 0 else "sell",
                    "priority": "high" if abs(difference) > 0.1 else "medium"
                })
        
        return recommendations
    
    def _calculate_strategy_risk_metrics(self, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate expected risk metrics for a strategy"""
        allocation = strategy["allocation"]
        
        # Expected volatility (simplified calculation)
        expected_volatility = (
            allocation.get("stocks", 0) * 0.20 +  # Stocks: 20% volatility
            allocation.get("bonds", 0) * 0.08 +   # Bonds: 8% volatility
            allocation.get("cash", 0) * 0.02      # Cash: 2% volatility
        )
        
        # Expected return (simplified calculation)
        expected_return = (
            allocation.get("stocks", 0) * 0.10 +  # Stocks: 10% return
            allocation.get("bonds", 0) * 0.05 +   # Bonds: 5% return
            allocation.get("cash", 0) * 0.03      # Cash: 3% return
        )
        
        return {
            "expected_volatility": expected_volatility,
            "expected_return": expected_return,
            "risk_adjusted_return": expected_return / expected_volatility if expected_volatility > 0 else 0
        }
    
    def _get_rebalancing_schedule(self, risk_tolerance: str) -> str:
        """Get recommended rebalancing schedule"""
        if risk_tolerance == "conservative":
            return "Quarterly"
        elif risk_tolerance == "moderate":
            return "Semi-annually"
        else:
            return "Annually"
    
    def _get_monitoring_frequency(self, risk_tolerance: str) -> str:
        """Get recommended monitoring frequency"""
        if risk_tolerance == "conservative":
            return "Weekly"
        elif risk_tolerance == "moderate":
            return "Bi-weekly"
        else:
            return "Monthly"
    
    async def _get_market_analysis(self) -> Dict[str, Any]:
        """Get current market analysis"""
        # This would typically come from external market data APIs
        # For now, return sample analysis
        return {
            "market_sentiment": "neutral",
            "volatility_index": 18.5,
            "sector_performance": {
                "technology": 0.15,
                "healthcare": 0.08,
                "financial": 0.05,
                "energy": -0.02
            },
            "economic_indicators": {
                "inflation": "moderate",
                "interest_rates": "rising",
                "gdp_growth": "positive"
            }
        }
    
    def _filter_opportunities_by_profile(self, market_analysis: Dict[str, Any], 
                                       risk_tolerance: str, investment_horizon: str) -> List[Dict[str, Any]]:
        """Filter market opportunities based on user profile"""
        opportunities = []
        
        # Add sample opportunities based on market conditions
        if market_analysis["market_sentiment"] == "bearish" and risk_tolerance in ["moderate", "aggressive"]:
            opportunities.append({
                "type": "dollar_cost_averaging",
                "description": "Market downturn presents buying opportunities",
                "risk_level": "medium",
                "potential_return": "high",
                "time_horizon": "long"
            })
        
        if "technology" in market_analysis["sector_performance"]:
            tech_performance = market_analysis["sector_performance"]["technology"]
            if tech_performance > 0.10 and risk_tolerance in ["aggressive", "growth"]:
                opportunities.append({
                    "type": "sector_rotation",
                    "description": "Technology sector showing strong momentum",
                    "risk_level": "high",
                    "potential_return": "high",
                    "time_horizon": "medium"
                })
        
        return opportunities
    
    def _rank_opportunities(self, opportunities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rank opportunities by potential return and risk"""
        for opp in opportunities:
            # Simple scoring system
            score = 0
            if opp["potential_return"] == "high":
                score += 3
            elif opp["potential_return"] == "medium":
                score += 2
            else:
                score += 1
            
            if opp["risk_level"] == "low":
                score += 3
            elif opp["risk_level"] == "medium":
                score += 2
            else:
                score += 1
            
            opp["score"] = score
        
        return sorted(opportunities, key=lambda x: x["score"], reverse=True)
    
    def _generate_action_recommendations(self, opportunities: List[Dict[str, Any]]) -> List[str]:
        """Generate specific action recommendations"""
        actions = []
        
        for opp in opportunities[:3]:  # Top 3 opportunities
            if opp["type"] == "dollar_cost_averaging":
                actions.append("Consider increasing monthly contributions to take advantage of lower prices")
            elif opp["type"] == "sector_rotation":
                actions.append("Review technology sector allocation and consider tactical overweight")
        
        return actions
    
    def _calculate_portfolio_health_score(self, asset_allocation: Dict[str, float], 
                                       risk_analysis: Dict[str, Any], 
                                       performance_analysis: Dict[str, Any]) -> float:
        """Calculate overall portfolio health score (0-100)"""
        score = 0
        
        # Diversification score (40 points)
        if "diversification_score" in risk_analysis:
            score += min(40, risk_analysis["diversification_score"] * 0.4)
        
        # Risk management (30 points)
        if risk_analysis.get("risk_level") == "low":
            score += 30
        elif risk_analysis.get("risk_level") == "moderate":
            score += 20
        else:
            score += 10
        
        # Performance (30 points)
        if performance_analysis.get("total_return_1y", 0) > 0.05:
            score += 30
        elif performance_analysis.get("total_return_1y", 0) > 0:
            score += 20
        else:
            score += 10
        
        return min(100, score) 