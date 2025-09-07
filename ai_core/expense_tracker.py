from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import pandas as pd
import asyncio

class ExpenseTracker:
    """Tracks and analyzes user expenses"""
    
    def __init__(self):
        # TODO: Initialize database connection
        pass
    
    async def get_user_expenses(self, user_id: str, days: int = 90) -> List[Dict[str, Any]]:
        """Get user expenses for the specified number of days"""
        # TODO: Implement database query
        # For now, return sample data
        return await self._get_sample_expenses(user_id, days)
    
    async def add_expense(self, user_id: str, expense_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new expense for a user"""
        try:
            # TODO: Implement database insertion
            expense = {
                "id": f"exp_{datetime.now().timestamp()}",
                "user_id": user_id,
                "amount": expense_data["amount"],
                "category": expense_data["category"],
                "description": expense_data.get("description", ""),
                "date": expense_data.get("date", datetime.now().isoformat()),
                "merchant": expense_data.get("merchant", ""),
                "payment_method": expense_data.get("payment_method", ""),
                "tags": expense_data.get("tags", [])
            }
            
            # TODO: Save to database
            return {"success": True, "expense": expense}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_expense_summary(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Get expense summary and analytics"""
        try:
            expenses = await self.get_user_expenses(user_id, days)
            
            if not expenses:
                return {"error": "No expenses found"}
            
            # Convert to DataFrame for analysis
            df = pd.DataFrame(expenses)
            df['date'] = pd.to_datetime(df['date'])
            df['amount'] = pd.to_numeric(df['amount'])
            
            # Calculate summary statistics
            total_spent = df['amount'].sum()
            avg_daily = df.groupby(df['date'].dt.date)['amount'].sum().mean()
            
            # Category breakdown
            category_totals = df.groupby('category')['amount'].sum().to_dict()
            category_percentages = {k: (v/total_spent)*100 for k, v in category_totals.items()}
            
            # Spending trends
            daily_spending = df.groupby(df['date'].dt.date)['amount'].sum()
            spending_trend = self._calculate_spending_trend(daily_spending)
            
            # Budget analysis
            budget_analysis = await self._analyze_budget_compliance(user_id, total_spent, days)
            
            return {
                "total_spent": float(total_spent),
                "avg_daily_spending": float(avg_daily),
                "category_breakdown": category_totals,
                "category_percentages": category_percentages,
                "spending_trend": spending_trend,
                "budget_analysis": budget_analysis,
                "expense_count": len(expenses),
                "period_days": days
            }
            
        except Exception as e:
            return {"error": f"Error generating expense summary: {str(e)}"}
    
    async def get_spending_patterns(self, user_id: str, days: int = 90) -> Dict[str, Any]:
        """Analyze spending patterns and identify trends"""
        try:
            expenses = await self.get_user_expenses(user_id, days)
            
            if not expenses:
                return {"error": "No expenses found"}
            
            df = pd.DataFrame(expenses)
            df['date'] = pd.to_datetime(df['date'])
            df['amount'] = pd.to_numeric(df['amount'])
            
            # Weekly patterns
            df['weekday'] = df['date'].dt.day_name()
            df['week'] = df['date'].dt.isocalendar().week
            
            weekly_patterns = df.groupby('weekday')['amount'].sum().to_dict()
            weekly_averages = df.groupby('weekday')['amount'].mean().to_dict()
            
            # Monthly patterns
            df['month'] = df['date'].dt.month
            monthly_totals = df.groupby('month')['amount'].sum().to_dict()
            
            # Time-based patterns
            df['hour'] = df['date'].dt.hour
            hourly_patterns = df.groupby('hour')['amount'].sum().to_dict()
            
            # Category trends over time
            category_trends = {}
            for category in df['category'].unique():
                category_data = df[df['category'] == category]
                category_trends[category] = {
                    "total": float(category_data['amount'].sum()),
                    "avg_per_transaction": float(category_data['amount'].mean()),
                    "transaction_count": len(category_data),
                    "trend": self._calculate_category_trend(category_data)
                }
            
            return {
                "weekly_patterns": weekly_patterns,
                "weekly_averages": weekly_averages,
                "monthly_totals": monthly_totals,
                "hourly_patterns": hourly_patterns,
                "category_trends": category_trends,
                "overall_trend": self._calculate_overall_trend(df)
            }
            
        except Exception as e:
            return {"error": f"Error analyzing spending patterns: {str(e)}"}
    
    async def get_budget_recommendations(self, user_id: str) -> Dict[str, Any]:
        """Generate budget recommendations based on spending patterns"""
        try:
            # Get current spending summary
            spending_summary = await self.get_expense_summary(user_id, 30)
            
            if "error" in spending_summary:
                return spending_summary
            
            # Get user's financial goals and constraints
            user_profile = await self._get_user_financial_profile(user_id)
            
            recommendations = []
            
            # Analyze category spending
            for category, percentage in spending_summary["category_percentages"].items():
                if percentage > 30:  # If any category is more than 30% of spending
                    recommendations.append({
                        "type": "category_reduction",
                        "category": category,
                        "current_percentage": percentage,
                        "recommended_percentage": 25,
                        "suggestion": f"Consider reducing {category} spending from {percentage:.1f}% to 25% of total expenses"
                    })
            
            # Analyze daily spending
            avg_daily = spending_summary["avg_daily_spending"]
            if avg_daily > user_profile.get("target_daily_spending", 100):
                recommendations.append({
                    "type": "daily_spending_reduction",
                    "current": avg_daily,
                    "target": user_profile.get("target_daily_spending", 100),
                    "suggestion": f"Reduce daily spending from ${avg_daily:.2f} to ${user_profile.get('target_daily_spending', 100):.2f}"
                })
            
            # Savings recommendations
            if spending_summary["total_spent"] > user_profile.get("monthly_budget", 3000):
                recommendations.append({
                    "type": "budget_overspending",
                    "current": spending_summary["total_spent"],
                    "budget": user_profile.get("monthly_budget", 3000),
                    "suggestion": "You're overspending your monthly budget. Consider reviewing discretionary expenses."
                })
            
            return {
                "recommendations": recommendations,
                "priority": self._prioritize_recommendations(recommendations),
                "estimated_savings": self._estimate_potential_savings(recommendations, spending_summary)
            }
            
        except Exception as e:
            return {"error": f"Error generating budget recommendations: {str(e)}"}
    
    def _calculate_spending_trend(self, daily_spending: pd.Series) -> str:
        """Calculate overall spending trend"""
        if len(daily_spending) < 7:
            return "insufficient_data"
        
        # Calculate trend using simple linear regression
        x = range(len(daily_spending))
        y = daily_spending.values
        
        # Simple trend calculation
        if len(y) > 1:
            trend_slope = (y[-1] - y[0]) / len(y)
            if trend_slope > 5:
                return "increasing"
            elif trend_slope < -5:
                return "decreasing"
            else:
                return "stable"
        
        return "stable"
    
    def _calculate_category_trend(self, category_data: pd.DataFrame) -> str:
        """Calculate trend for a specific category"""
        if len(category_data) < 3:
            return "insufficient_data"
        
        # Group by week and calculate trend
        weekly_totals = category_data.groupby(category_data['date'].dt.isocalendar().week)['amount'].sum()
        
        if len(weekly_totals) > 1:
            trend_slope = (weekly_totals.iloc[-1] - weekly_totals.iloc[0]) / len(weekly_totals)
            if trend_slope > 10:
                return "increasing"
            elif trend_slope < -10:
                return "decreasing"
            else:
                return "stable"
        
        return "stable"
    
    def _calculate_overall_trend(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate overall spending trend with more detail"""
        if len(df) < 7:
            return {"trend": "insufficient_data"}
        
        # Calculate moving averages
        df_sorted = df.sort_values('date')
        df_sorted['moving_avg_7d'] = df_sorted['amount'].rolling(window=7).mean()
        df_sorted['moving_avg_30d'] = df_sorted['amount'].rolling(window=30).mean()
        
        # Get latest values
        latest_7d = df_sorted['moving_avg_7d'].iloc[-1]
        latest_30d = df_sorted['moving_avg_30d'].iloc[-1]
        
        if pd.isna(latest_7d) or pd.isna(latest_30d):
            return {"trend": "insufficient_data"}
        
        # Compare short-term vs long-term
        if latest_7d > latest_30d * 1.1:
            trend = "accelerating"
        elif latest_7d < latest_30d * 0.9:
            trend = "decelerating"
        else:
            trend = "stable"
        
        return {
            "trend": trend,
            "short_term_avg": float(latest_7d),
            "long_term_avg": float(latest_30d),
            "volatility": float(df_sorted['amount'].std())
        }
    
    async def _analyze_budget_compliance(self, user_id: str, total_spent: float, days: int) -> Dict[str, Any]:
        """Analyze how well the user is sticking to their budget"""
        # TODO: Get user's budget from database
        monthly_budget = 3000  # Default value
        
        # Calculate daily budget
        daily_budget = monthly_budget / 30
        actual_daily = total_spent / days
        
        compliance_percentage = (daily_budget / actual_daily) * 100 if actual_daily > 0 else 100
        
        return {
            "monthly_budget": monthly_budget,
            "daily_budget": daily_budget,
            "actual_daily_spending": actual_daily,
            "compliance_percentage": min(100, compliance_percentage),
            "status": "under_budget" if compliance_percentage >= 100 else "over_budget"
        }
    
    async def _get_user_financial_profile(self, user_id: str) -> Dict[str, Any]:
        """Get user's financial profile and goals"""
        # TODO: Implement database query
        return {
            "monthly_budget": 3000,
            "target_daily_spending": 100,
            "savings_goal": 500,
            "risk_tolerance": "moderate",
            "financial_goals": ["emergency_fund", "retirement", "vacation"]
        }
    
    def _prioritize_recommendations(self, recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prioritize recommendations by impact and urgency"""
        # Simple prioritization based on type and impact
        priority_scores = {
            "budget_overspending": 3,
            "category_reduction": 2,
            "daily_spending_reduction": 1
        }
        
        for rec in recommendations:
            rec["priority_score"] = priority_scores.get(rec["type"], 0)
        
        return sorted(recommendations, key=lambda x: x["priority_score"], reverse=True)
    
    def _estimate_potential_savings(self, recommendations: List[Dict[str, Any]], spending_summary: Dict[str, Any]) -> float:
        """Estimate potential savings from following recommendations"""
        total_savings = 0.0
        
        for rec in recommendations:
            if rec["type"] == "category_reduction":
                category = rec["category"]
                current_amount = spending_summary["category_breakdown"].get(category, 0)
                target_percentage = rec["recommended_percentage"]
                current_percentage = rec["current_percentage"]
                
                if current_percentage > target_percentage:
                    savings = current_amount * (current_percentage - target_percentage) / current_percentage
                    total_savings += savings
            
            elif rec["type"] == "daily_spending_reduction":
                daily_savings = rec["current"] - rec["target"]
                total_savings += daily_savings * 30  # Monthly savings
        
        return total_savings
    
    async def _get_sample_expenses(self, user_id: str, days: int) -> List[Dict[str, Any]]:
        """Get sample expense data for development/testing"""
        categories = ["Food & Dining", "Transportation", "Shopping", "Entertainment", "Bills & Utilities", "Healthcare"]
        merchants = ["Walmart", "Target", "Amazon", "Uber", "Netflix", "Electric Company", "Gas Station"]
        
        expenses = []
        base_date = datetime.now()
        
        for i in range(days):
            # Generate 1-5 expenses per day
            daily_expenses = random.randint(1, 5)
            
            for j in range(daily_expenses):
                expense_date = base_date - timedelta(days=i)
                category = random.choice(categories)
                merchant = random.choice(merchants)
                
                # Generate realistic amounts based on category
                if category == "Food & Dining":
                    amount = random.uniform(8, 45)
                elif category == "Transportation":
                    amount = random.uniform(15, 80)
                elif category == "Shopping":
                    amount = random.uniform(20, 150)
                elif category == "Entertainment":
                    amount = random.uniform(10, 60)
                elif category == "Bills & Utilities":
                    amount = random.uniform(50, 200)
                else:
                    amount = random.uniform(10, 100)
                
                expenses.append({
                    "id": f"exp_{i}_{j}",
                    "user_id": user_id,
                    "amount": round(amount, 2),
                    "category": category,
                    "description": f"{category} expense",
                    "date": expense_date.isoformat(),
                    "merchant": merchant,
                    "payment_method": random.choice(["Credit Card", "Debit Card", "Cash"]),
                    "tags": [category.lower().replace(" & ", "_").replace(" ", "_")]
                })
        
        return expenses

# Add missing import
import random 