from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import asyncio

class FinancialForecaster:
    """Forecasts financial health and cash flow projections"""
    
    def __init__(self):
        # Forecasting parameters
        self.forecast_horizons = [30, 90, 180, 365]  # days
        self.confidence_levels = [0.68, 0.95, 0.99]  # 1σ, 2σ, 3σ
        
        # Economic scenario assumptions
        self.economic_scenarios = {
            "baseline": {
                "inflation_rate": 0.025,  # 2.5% annual
                "interest_rate": 0.05,    # 5% annual
                "market_return": 0.08,    # 8% annual
                "probability": 0.6
            },
            "optimistic": {
                "inflation_rate": 0.02,   # 2% annual
                "interest_rate": 0.04,    # 4% annual
                "market_return": 0.12,    # 12% annual
                "probability": 0.2
            },
            "pessimistic": {
                "inflation_rate": 0.04,   # 4% annual
                "interest_rate": 0.07,    # 7% annual
                "market_return": 0.04,    # 4% annual
                "probability": 0.2
            }
        }
    
    async def generate_forecast(self, financial_data: Dict[str, Any], 
                              expenses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive financial forecast"""
        try:
            forecast = {
                "cash_flow_forecast": {},
                "net_worth_projection": {},
                "expense_forecast": {},
                "investment_returns": {},
                "risk_scenarios": {},
                "recommendations": []
            }
            
            # Generate cash flow forecast
            forecast["cash_flow_forecast"] = await self._forecast_cash_flow(
                financial_data, expenses
            )
            
            # Project net worth
            forecast["net_worth_projection"] = await self._project_net_worth(
                financial_data, forecast["cash_flow_forecast"]
            )
            
            # Forecast expenses
            forecast["expense_forecast"] = await self._forecast_expenses(expenses)
            
            # Project investment returns
            forecast["investment_returns"] = await self._project_investment_returns(
                financial_data
            )
            
            # Generate risk scenarios
            forecast["risk_scenarios"] = await self._generate_risk_scenarios(
                forecast, financial_data
            )
            
            # Generate recommendations
            forecast["recommendations"] = await self._generate_forecast_recommendations(
                forecast
            )
            
            return forecast
            
        except Exception as e:
            return {"error": f"Error generating forecast: {str(e)}"}
    
    async def _forecast_cash_flow(self, financial_data: Dict[str, Any], 
                                 expenses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Forecast cash flow for different time horizons"""
        try:
            cash_flow_forecast = {}
            
            # Get current financial position
            current_income = financial_data.get("monthly_income", 5000)
            current_expenses = sum(exp.get("amount", 0) for exp in expenses if 
                                 exp.get("date", "") >= (datetime.now() - timedelta(days=30)).isoformat())
            
            # Calculate current cash flow
            current_cash_flow = current_income - current_expenses
            
            for horizon in self.forecast_horizons:
                # Project income growth (assume 3% annual growth)
                income_growth_rate = 0.03 / 365  # Daily rate
                projected_income = current_income * (1 + income_growth_rate * horizon)
                
                # Project expense growth (assume 2% annual inflation)
                expense_inflation_rate = 0.02 / 365  # Daily rate
                projected_expenses = current_expenses * (1 + expense_inflation_rate * horizon)
                
                # Calculate projected cash flow
                projected_cash_flow = projected_income - projected_expenses
                
                # Calculate cumulative cash flow
                cumulative_cash_flow = current_cash_flow + (projected_cash_flow * horizon / 30)
                
                cash_flow_forecast[f"{horizon}_days"] = {
                    "projected_income": round(projected_income, 2),
                    "projected_expenses": round(projected_expenses, 2),
                    "monthly_cash_flow": round(projected_cash_flow, 2),
                    "cumulative_cash_flow": round(cumulative_cash_flow, 2),
                    "cash_flow_ratio": round(projected_cash_flow / projected_expenses, 2) if projected_expenses > 0 else 0
                }
            
            return cash_flow_forecast
            
        except Exception as e:
            return {"error": f"Error forecasting cash flow: {str(e)}"}
    
    async def _project_net_worth(self, financial_data: Dict[str, Any], 
                                cash_flow_forecast: Dict[str, Any]) -> Dict[str, Any]:
        """Project net worth over time"""
        try:
            net_worth_projection = {}
            
            # Get current net worth components
            current_assets = financial_data.get("total_assets", 100000)
            current_liabilities = financial_data.get("total_liabilities", 25000)
            current_net_worth = current_assets - current_liabilities
            
            # Get portfolio value
            portfolio_value = financial_data.get("portfolio", {}).get("total_value", 50000)
            
            for horizon in self.forecast_horizons:
                # Project asset growth
                # Assume portfolio grows at market rate + contributions
                market_growth_rate = 0.08 / 365  # Daily rate
                daily_contribution = cash_flow_forecast.get(f"{horizon}_days", {}).get("monthly_cash_flow", 0) / 30
                
                # Project portfolio growth
                projected_portfolio = portfolio_value * (1 + market_growth_rate * horizon)
                
                # Add cumulative contributions
                cumulative_contributions = daily_contribution * horizon
                projected_portfolio += cumulative_contributions
                
                # Project other assets (assume 2% annual growth)
                other_assets = current_assets - portfolio_value
                other_assets_growth = 0.02 / 365
                projected_other_assets = other_assets * (1 + other_assets_growth * horizon)
                
                # Project liabilities (assume gradual reduction)
                liability_reduction_rate = 0.05 / 365  # 5% annual reduction
                projected_liabilities = max(0, current_liabilities * (1 - liability_reduction_rate * horizon))
                
                # Calculate projected net worth
                projected_assets = projected_portfolio + projected_other_assets
                projected_net_worth = projected_assets - projected_liabilities
                
                net_worth_projection[f"{horizon}_days"] = {
                    "projected_assets": round(projected_assets, 2),
                    "projected_portfolio": round(projected_portfolio, 2),
                    "projected_liabilities": round(projected_liabilities, 2),
                    "projected_net_worth": round(projected_net_worth, 2),
                    "net_worth_change": round(projected_net_worth - current_net_worth, 2),
                    "growth_rate": round(((projected_net_worth / current_net_worth) - 1) * 100, 2) if current_net_worth > 0 else 0
                }
            
            return net_worth_projection
            
        except Exception as e:
            return {"error": f"Error projecting net worth: {str(e)}"}
    
    async def _forecast_expenses(self, expenses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Forecast future expenses based on historical patterns"""
        try:
            if not expenses:
                return {"error": "No expense data available"}
            
            # Convert to DataFrame for analysis
            df = pd.DataFrame(expenses)
            df['date'] = pd.to_datetime(df['date'])
            df['amount'] = pd.to_numeric(df['amount'])
            
            # Calculate daily expense patterns
            daily_expenses = df.groupby(df['date'].dt.date)['amount'].sum()
            
            # Calculate moving averages
            if len(daily_expenses) >= 7:
                moving_avg_7d = daily_expenses.rolling(window=7).mean()
                moving_avg_30d = daily_expenses.rolling(window=30).mean()
            else:
                moving_avg_7d = daily_expenses.mean()
                moving_avg_30d = daily_expenses.mean()
            
            # Calculate expense volatility
            expense_volatility = daily_expenses.std() if len(daily_expenses) > 1 else 0
            
            # Project future expenses
            expense_forecast = {}
            current_avg = moving_avg_30d.iloc[-1] if hasattr(moving_avg_30d, 'iloc') else moving_avg_30d
            
            for horizon in self.forecast_horizons:
                # Assume expenses grow with inflation
                inflation_rate = 0.02 / 365  # Daily rate
                projected_daily_expense = current_avg * (1 + inflation_rate * horizon)
                
                # Calculate confidence intervals
                confidence_intervals = {}
                for confidence in self.confidence_levels:
                    if confidence == 0.68:
                        z_score = 1.0
                    elif confidence == 0.95:
                        z_score = 1.96
                    else:
                        z_score = 2.58
                    
                    margin_of_error = z_score * expense_volatility / np.sqrt(horizon) if horizon > 0 else 0
                    confidence_intervals[f"{int(confidence*100)}%"] = {
                        "lower": max(0, projected_daily_expense - margin_of_error),
                        "upper": projected_daily_expense + margin_of_error
                    }
                
                expense_forecast[f"{horizon}_days"] = {
                    "projected_daily_expense": round(projected_daily_expense, 2),
                    "projected_monthly_expense": round(projected_daily_expense * 30, 2),
                    "confidence_intervals": confidence_intervals,
                    "volatility": round(expense_volatility, 2)
                }
            
            return expense_forecast
            
        except Exception as e:
            return {"error": f"Error forecasting expenses: {str(e)}"}
    
    async def _project_investment_returns(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Project investment returns under different scenarios"""
        try:
            investment_returns = {}
            portfolio = financial_data.get("portfolio", {})
            current_portfolio_value = portfolio.get("total_value", 50000)
            
            for scenario_name, scenario_params in self.economic_scenarios.items():
                scenario_returns = {}
                
                for horizon in self.forecast_horizons:
                    # Calculate daily return rate
                    daily_return_rate = scenario_params["market_return"] / 365
                    
                    # Project portfolio value
                    projected_value = current_portfolio_value * (1 + daily_return_rate * horizon)
                    
                    # Calculate returns
                    total_return = projected_value - current_portfolio_value
                    annualized_return = ((projected_value / current_portfolio_value) ** (365 / horizon) - 1) if horizon > 0 else 0
                    
                    # Adjust for inflation
                    inflation_rate = scenario_params["inflation_rate"] / 365
                    real_return = total_return - (current_portfolio_value * inflation_rate * horizon)
                    
                    scenario_returns[f"{horizon}_days"] = {
                        "projected_value": round(projected_value, 2),
                        "total_return": round(total_return, 2),
                        "annualized_return": round(annualized_return * 100, 2),
                        "real_return": round(real_return, 2),
                        "probability": scenario_params["probability"]
                    }
                
                investment_returns[scenario_name] = scenario_returns
            
            return investment_returns
            
        except Exception as e:
            return {"error": f"Error projecting investment returns: {str(e)}"}
    
    async def _generate_risk_scenarios(self, forecast: Dict[str, Any], 
                                     financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate risk scenarios and stress tests"""
        try:
            risk_scenarios = {}
            
            # Market crash scenario
            market_crash = await self._simulate_market_crash(forecast, financial_data)
            risk_scenarios["market_crash"] = market_crash
            
            # Job loss scenario
            job_loss = await self._simulate_job_loss(forecast, financial_data)
            risk_scenarios["job_loss"] = job_loss
            
            # Medical emergency scenario
            medical_emergency = await self._simulate_medical_emergency(forecast, financial_data)
            risk_scenarios["medical_emergency"] = medical_emergency
            
            # Interest rate shock scenario
            interest_rate_shock = await self._simulate_interest_rate_shock(forecast, financial_data)
            risk_scenarios["interest_rate_shock"] = interest_rate_shock
            
            return risk_scenarios
            
        except Exception as e:
            return {"error": f"Error generating risk scenarios: {str(e)}"}
    
    async def _simulate_market_crash(self, forecast: Dict[str, Any], 
                                   financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate impact of a market crash"""
        try:
            portfolio_value = financial_data.get("portfolio", {}).get("total_value", 50000)
            
            # Assume 30% market crash
            crash_impact = 0.30
            new_portfolio_value = portfolio_value * (1 - crash_impact)
            
            # Calculate impact on net worth
            net_worth_impact = portfolio_value * crash_impact
            
            # Calculate recovery time (assume 5 years to recover)
            recovery_years = 5
            recovery_months = recovery_years * 12
            
            return {
                "scenario": "30% Market Crash",
                "portfolio_loss": round(net_worth_impact, 2),
                "new_portfolio_value": round(new_portfolio_value, 2),
                "recovery_time_months": recovery_months,
                "monthly_recovery_amount": round(net_worth_impact / recovery_months, 2),
                "risk_level": "high",
                "mitigation_strategies": [
                    "Maintain emergency fund",
                    "Diversify across asset classes",
                    "Consider defensive stocks",
                    "Dollar-cost averaging during recovery"
                ]
            }
            
        except Exception as e:
            return {"error": f"Error simulating market crash: {str(e)}"}
    
    async def _simulate_job_loss(self, forecast: Dict[str, Any], 
                                financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate impact of job loss"""
        try:
            monthly_income = financial_data.get("monthly_income", 5000)
            emergency_fund = financial_data.get("emergency_fund", 15000)
            
            # Calculate survival time with current emergency fund
            monthly_expenses = forecast.get("expense_forecast", {}).get("30_days", {}).get("projected_monthly_expense", 3000)
            survival_months = emergency_fund / monthly_expenses if monthly_expenses > 0 else 0
            
            # Calculate required emergency fund (6 months of expenses)
            required_emergency_fund = monthly_expenses * 6
            
            return {
                "scenario": "Job Loss",
                "monthly_income_loss": monthly_income,
                "current_emergency_fund": emergency_fund,
                "monthly_expenses": monthly_expenses,
                "survival_months": round(survival_months, 1),
                "required_emergency_fund": round(required_emergency_fund, 2),
                "funding_gap": round(required_emergency_fund - emergency_fund, 2),
                "risk_level": "medium" if survival_months >= 3 else "high",
                "mitigation_strategies": [
                    "Build emergency fund to 6 months of expenses",
                    "Reduce discretionary spending",
                    "Consider side income sources",
                    "Review insurance coverage"
                ]
            }
            
        except Exception as e:
            return {"error": f"Error simulating job loss: {str(e)}"}
    
    async def _simulate_medical_emergency(self, forecast: Dict[str, Any], 
                                         financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate impact of medical emergency"""
        try:
            # Assume $10,000 medical emergency
            medical_cost = 10000
            health_insurance_coverage = financial_data.get("health_insurance_coverage", 0.8)
            
            # Calculate out-of-pocket cost
            out_of_pocket = medical_cost * (1 - health_insurance_coverage)
            
            # Check if emergency fund can cover it
            emergency_fund = financial_data.get("emergency_fund", 15000)
            can_cover = emergency_fund >= out_of_pocket
            
            return {
                "scenario": "Medical Emergency ($10,000)",
                "total_cost": medical_cost,
                "insurance_coverage": health_insurance_coverage,
                "out_of_pocket_cost": round(out_of_pocket, 2),
                "emergency_fund": emergency_fund,
                "can_cover": can_cover,
                "funding_gap": round(max(0, out_of_pocket - emergency_fund), 2),
                "risk_level": "low" if can_cover else "high",
                "mitigation_strategies": [
                    "Ensure adequate health insurance",
                    "Build emergency fund",
                    "Consider health savings account",
                    "Review medical expense budget"
                ]
            }
            
        except Exception as e:
            return {"error": f"Error simulating medical emergency: {str(e)}"}
    
    async def _simulate_interest_rate_shock(self, forecast: Dict[str, Any], 
                                           financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate impact of interest rate shock"""
        try:
            # Assume 2% interest rate increase
            rate_increase = 0.02
            current_liabilities = financial_data.get("total_liabilities", 25000)
            
            # Calculate additional interest cost
            additional_interest = current_liabilities * rate_increase
            
            # Impact on monthly payments (assume 30-year loans)
            monthly_payment_increase = additional_interest / 12
            
            return {
                "scenario": "2% Interest Rate Increase",
                "rate_increase": rate_increase,
                "additional_annual_interest": round(additional_interest, 2),
                "monthly_payment_increase": round(monthly_payment_increase, 2),
                "risk_level": "medium",
                "mitigation_strategies": [
                    "Refinance high-interest debt",
                    "Pay down variable-rate loans",
                    "Lock in fixed rates",
                    "Build emergency fund for higher payments"
                ]
            }
            
        except Exception as e:
            return {"error": f"Error simulating interest rate shock: {str(e)}"}
    
    async def _generate_forecast_recommendations(self, forecast: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate actionable recommendations based on forecast"""
        try:
            recommendations = []
            
            # Cash flow recommendations
            cash_flow_forecast = forecast.get("cash_flow_forecast", {})
            if cash_flow_forecast:
                for horizon, data in cash_flow_forecast.items():
                    if data.get("cash_flow_ratio", 0) < 0.2:  # Less than 20% positive cash flow
                        recommendations.append({
                            "category": "cash_flow",
                            "priority": "high",
                            "title": "Improve Cash Flow",
                            "description": f"Cash flow ratio is {data['cash_flow_ratio']:.1%} for {horizon}",
                            "action": "Review expenses and increase income sources",
                            "timeline": "immediate"
                        })
            
            # Net worth recommendations
            net_worth_projection = forecast.get("net_worth_projection", {})
            if net_worth_projection:
                for horizon, data in net_worth_projection.items():
                    if data.get("growth_rate", 0) < 5:  # Less than 5% annual growth
                        recommendations.append({
                            "category": "net_worth",
                            "priority": "medium",
                            "title": "Accelerate Net Worth Growth",
                            "description": f"Projected growth rate is {data['growth_rate']:.1f}% for {horizon}",
                            "action": "Increase savings rate and optimize investments",
                            "timeline": "3-6 months"
                        })
            
            # Risk management recommendations
            risk_scenarios = forecast.get("risk_scenarios", {})
            if risk_scenarios:
                for scenario_name, scenario_data in risk_scenarios.items():
                    if scenario_data.get("risk_level") == "high":
                        recommendations.append({
                            "category": "risk_management",
                            "priority": "high",
                            "title": f"Mitigate {scenario_name.replace('_', ' ').title()} Risk",
                            "description": f"High risk level identified for {scenario_name}",
                            "action": scenario_data.get("mitigation_strategies", ["Review risk exposure"])[0],
                            "timeline": "immediate"
                        })
            
            return recommendations
            
        except Exception as e:
            return [{"error": f"Error generating recommendations: {str(e)}"}] 