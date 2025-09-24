import asyncio
import asyncpg
import os
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, date
from decimal import Decimal
import json
import uuid
import logging
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Centralized database connection and query manager"""
    
    def __init__(self):
        self.pool = None
        self.db_config = {
            'user': os.getenv('POSTGRES_USER', 'amrutha'),
            'password': os.getenv('POSTGRES_PASSWORD', 'vamru'),
            'host': os.getenv('POSTGRES_HOST', 'localhost'),
            'port': os.getenv('POSTGRES_PORT', '5432'),
            'database': os.getenv('POSTGRES_DB', 'project'),
            'min_size': int(os.getenv('DB_POOL_MIN_SIZE', '5')),
            'max_size': int(os.getenv('DB_POOL_MAX_SIZE', '20'))
        }
    
    async def initialize(self):
        """Initialize database connection pool"""
        try:
            self.pool = await asyncpg.create_pool(**self.db_config)
            logger.info("✅ Database connection pool initialized")
            
            # Test connection
            async with self.pool.acquire() as conn:
                await conn.fetchval('SELECT 1')
            logger.info("✅ Database connection test successful")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize database: {e}")
            raise e
    
    async def close(self):
        """Close database connection pool"""
        if self.pool:
            await self.pool.close()
            logger.info("✅ Database connection pool closed")
    
    @asynccontextmanager
    async def get_connection(self):
        """Get database connection from pool"""
        if not self.pool:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        
        async with self.pool.acquire() as conn:
            yield conn
    
    # User Profile Methods
    async def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user financial profile"""
        async with self.get_connection() as conn:
            # Try to convert user_id to int, if it fails, treat as username
            try:
                user_id_int = int(user_id)
                row = await conn.fetchrow("""
                    SELECT up.*, u.username, u.email, u.first_name, u.last_name
                    FROM core_userprofile up
                    JOIN auth_user u ON up.user_id = u.id
                    WHERE u.id = $1
                """, user_id_int)
            except ValueError:
                # user_id is not a number, treat as username
                row = await conn.fetchrow("""
                    SELECT up.*, u.username, u.email, u.first_name, u.last_name
                    FROM core_userprofile up
                    JOIN auth_user u ON up.user_id = u.id
                    WHERE u.username = $1
                """, user_id)
            
            if row:
                return dict(row)
            return None
    
    async def create_user_profile(self, user_id: str, profile_data: Dict[str, Any]) -> bool:
        """Create user financial profile"""
        try:
            async with self.get_connection() as conn:
                await conn.execute("""
                    INSERT INTO core_userprofile (
                        user_id, monthly_income, monthly_budget, target_daily_spending,
                        savings_goal, risk_tolerance, investment_horizon, age
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                    ON CONFLICT (user_id) DO UPDATE SET
                        monthly_income = EXCLUDED.monthly_income,
                        monthly_budget = EXCLUDED.monthly_budget,
                        target_daily_spending = EXCLUDED.target_daily_spending,
                        savings_goal = EXCLUDED.savings_goal,
                        risk_tolerance = EXCLUDED.risk_tolerance,
                        investment_horizon = EXCLUDED.investment_horizon,
                        age = EXCLUDED.age,
                        updated_at = NOW()
                """, 
                user_id,
                profile_data.get('monthly_income', 0),
                profile_data.get('monthly_budget', 3000),
                profile_data.get('target_daily_spending', 100),
                profile_data.get('savings_goal', 500),
                profile_data.get('risk_tolerance', 'moderate'),
                profile_data.get('investment_horizon', 'long_term'),
                profile_data.get('age', 35)
                )
                return True
        except Exception as e:
            logger.error(f"Error creating user profile: {e}")
            return False
    
    # Expense Methods
    async def get_user_expenses(self, user_id: str, days: int = 90) -> List[Dict[str, Any]]:
        """Get user expenses for specified days"""
        async with self.get_connection() as conn:
            # Try to convert user_id to int, if it fails, treat as username
            try:
                user_id_int = int(user_id)
                rows = await conn.fetch("""
                    SELECT e.*, ec.name as category_name, ec.color as category_color
                    FROM core_expense e
                    JOIN core_expensecategory ec ON e.category_id = ec.id
                    JOIN auth_user u ON e.user_id = u.id
                    WHERE u.id = $1
                    AND e.date >= NOW() - ($2 || ' days')::INTERVAL
                    ORDER BY e.date DESC
                """, user_id_int, str(days))
            except ValueError:
                # user_id is not a number, treat as username
                rows = await conn.fetch("""
                    SELECT e.*, ec.name as category_name, ec.color as category_color
                    FROM core_expense e
                    JOIN core_expensecategory ec ON e.category_id = ec.id
                    JOIN auth_user u ON e.user_id = u.id
                    WHERE u.username = $1
                    AND e.date >= NOW() - ($2 || ' days')::INTERVAL
                    ORDER BY e.date DESC
                """, user_id, str(days))
            
            return [dict(row) for row in rows]
    
    async def add_expense(self, user_id: str, expense_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Add new expense"""
        try:
            async with self.get_connection() as conn:
                # Resolve user id if a username was provided
                resolved_user_id = await self._resolve_user_id(conn, user_id)
                # Normalize and validate incoming fields
                normalized = self._normalize_expense_input(expense_data)
                # Get or create category
                category_id = await self._get_or_create_category(conn, normalized['category'])
                
                # Insert expense
                expense_uuid = uuid.uuid4()
                row = await conn.fetchrow("""
                    INSERT INTO core_expense (
                        id, user_id, amount, category_id, description, merchant,
                        payment_method, date, tags, is_recurring, recurring_frequency,
                        created_at, updated_at
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
                    RETURNING *
                """,
                str(expense_uuid),
                resolved_user_id,
                normalized['amount'],
                category_id,
                normalized['description'],
                normalized['merchant'],
                normalized['payment_method'],
                normalized['date'],
                json.dumps(normalized['tags']),
                normalized['is_recurring'],
                normalized['recurring_frequency'],
                datetime.now(),
                datetime.now()
                )
                
                return dict(row)
        except Exception as e:
            logger.error(f"Error adding expense: {e}")
            return None
    
    async def get_expense_summary(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Get expense summary and analytics"""
        async with self.get_connection() as conn:
            # Try to convert user_id to int, if it fails, treat as username
            try:
                user_id_int = int(user_id)
                # Get total spending
                total_spent = await conn.fetchval("""
                    SELECT COALESCE(SUM(amount), 0)
                    FROM core_expense e
                    JOIN auth_user u ON e.user_id = u.id
                    WHERE u.id = $1
                    AND e.date >= NOW() - ($2 || ' days')::INTERVAL
                """, user_id_int, str(days))
            except ValueError:
                # user_id is not a number, treat as username
                total_spent = await conn.fetchval("""
                    SELECT COALESCE(SUM(amount), 0)
                    FROM core_expense e
                    JOIN auth_user u ON e.user_id = u.id
                    WHERE u.username = $1
                    AND e.date >= NOW() - ($2 || ' days')::INTERVAL
                """, user_id, str(days))
            # Normalize aggregate to float for further calculations
            total_spent = float(total_spent or 0)
            
            # Get category breakdown
            try:
                user_id_int = int(user_id)
                category_rows = await conn.fetch("""
                    SELECT ec.name as category, SUM(e.amount) as total, COUNT(*) as count
                    FROM core_expense e
                    JOIN core_expensecategory ec ON e.category_id = ec.id
                    JOIN auth_user u ON e.user_id = u.id
                    WHERE u.id = $1
                    AND e.date >= NOW() - ($2 || ' days')::INTERVAL
                    GROUP BY ec.name
                    ORDER BY total DESC
                """, user_id_int, str(days))
                
                # Get daily averages
                daily_avg = await conn.fetchval("""
                    SELECT COALESCE(AVG(daily_total), 0)
                    FROM (
                        SELECT DATE(e.date) as day, SUM(e.amount) as daily_total
                        FROM core_expense e
                        JOIN auth_user u ON e.user_id = u.id
                        WHERE u.id = $1
                        AND e.date >= NOW() - ($2 || ' days')::INTERVAL
                        GROUP BY DATE(e.date)
                    ) daily_totals
                """, user_id_int, str(days))
            except ValueError:
                # user_id is not a number, treat as username
                category_rows = await conn.fetch("""
                    SELECT ec.name as category, SUM(e.amount) as total, COUNT(*) as count
                    FROM core_expense e
                    JOIN core_expensecategory ec ON e.category_id = ec.id
                    JOIN auth_user u ON e.user_id = u.id
                    WHERE u.username = $1
                    AND e.date >= NOW() - ($2 || ' days')::INTERVAL
                    GROUP BY ec.name
                    ORDER BY total DESC
                """, user_id, str(days))
                
                # Get daily averages
                daily_avg = await conn.fetchval("""
                    SELECT COALESCE(AVG(daily_total), 0)
                    FROM (
                        SELECT DATE(e.date) as day, SUM(e.amount) as daily_total
                        FROM core_expense e
                        JOIN auth_user u ON e.user_id = u.id
                        WHERE u.username = $1
                        AND e.date >= NOW() - ($2 || ' days')::INTERVAL
                        GROUP BY DATE(e.date)
                    ) daily_totals
                """, user_id, str(days))
            # Normalize aggregate to float
            daily_avg = float(daily_avg or 0)
            
            category_breakdown = {row['category']: float(row['total']) for row in category_rows}
            category_percentages = {
                category: (amount / total_spent * 100) if total_spent > 0 else 0
                for category, amount in category_breakdown.items()
            }
            
            return {
                'total_spent': total_spent,
                'avg_daily_spending': daily_avg,
                'category_breakdown': category_breakdown,
                'category_percentages': category_percentages,
                'expense_count': sum(row['count'] for row in category_rows),
                'period_days': days
            }
    
    # Investment Methods
    async def get_user_investments(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user investment accounts and holdings"""
        async with self.get_connection() as conn:
            # Try to convert user_id to int, if it fails, treat as username
            try:
                user_id_int = int(user_id)
                # Get investment accounts
                accounts = await conn.fetch("""
                    SELECT ia.*
                    FROM core_investmentaccount ia
                    JOIN auth_user u ON ia.user_id = u.id
                    WHERE u.id = $1
                    AND ia.is_active = true
                    ORDER BY ia.created_at DESC
                """, user_id_int)
            except ValueError:
                # user_id is not a number, treat as username
                accounts = await conn.fetch("""
                    SELECT ia.*
                    FROM core_investmentaccount ia
                    JOIN auth_user u ON ia.user_id = u.id
                    WHERE u.username = $1
                    AND ia.is_active = true
                    ORDER BY ia.created_at DESC
                """, user_id)
            
            result = []
            for account in accounts:
                account_dict = dict(account)
                
                # Get investments for this account
                investments = await conn.fetch("""
                    SELECT *
                    FROM core_investment
                    WHERE account_id = $1 AND is_active = true
                    ORDER BY created_at DESC
                """, account['id'])
                
                account_dict['investments'] = [dict(inv) for inv in investments]
                result.append(account_dict)
            
            return result
    
    async def add_investment(self, user_id: str, account_id: str, investment_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Add new investment"""
        try:
            async with self.get_connection() as conn:
                row = await conn.fetchrow("""
                    INSERT INTO core_investment (
                        account_id, symbol, name, asset_type, quantity,
                        purchase_price, current_price, purchase_date
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                    RETURNING *
                """,
                account_id,
                investment_data['symbol'],
                investment_data['name'],
                investment_data.get('asset_type', 'stock'),
                investment_data['quantity'],
                investment_data['purchase_price'],
                investment_data.get('current_price', investment_data['purchase_price']),
                investment_data.get('purchase_date', date.today())
                )
                
                return dict(row)
        except Exception as e:
            logger.error(f"Error adding investment: {e}")
            return None
    
    # Financial Goals Methods
    async def get_user_goals(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user financial goals"""
        async with self.get_connection() as conn:
            # Try to convert user_id to int, if it fails, treat as username
            try:
                user_id_int = int(user_id)
                rows = await conn.fetch("""
                    SELECT *
                    FROM core_financialgoal
                    WHERE user_id = $1
                    ORDER BY priority DESC, target_date ASC
                """, user_id_int)
            except ValueError:
                # user_id is not a number, treat as username
                rows = await conn.fetch("""
                    SELECT *
                    FROM core_financialgoal
                    WHERE user_id = (SELECT id FROM auth_user WHERE username = $1)
                    ORDER BY priority DESC, target_date ASC
                """, user_id)
            
            return [dict(row) for row in rows]
    
    async def add_financial_goal(self, user_id: str, goal_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Add new financial goal"""
        try:
            async with self.get_connection() as conn:
                row = await conn.fetchrow("""
                    INSERT INTO core_financialgoal (
                        user_id, goal_name, goal_type, target_amount,
                        current_amount, target_date, priority
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                    RETURNING *
                """,
                user_id,
                goal_data['goal_name'],
                goal_data['goal_type'],
                goal_data['target_amount'],
                goal_data.get('current_amount', 0),
                goal_data['target_date'],
                goal_data.get('priority', 'medium')
                )
                
                return dict(row)
        except Exception as e:
            logger.error(f"Error adding financial goal: {e}")
            return None
    
    # Budget Methods
    async def get_user_budgets(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user budget settings"""
        async with self.get_connection() as conn:
            # Try to convert user_id to int, if it fails, treat as username
            try:
                user_id_int = int(user_id)
                rows = await conn.fetch("""
                    SELECT b.*, ec.name as category_name, ec.color as category_color
                    FROM core_budget b
                    JOIN core_expensecategory ec ON b.category_id = ec.id
                    JOIN auth_user u ON b.user_id = u.id
                    WHERE u.id = $1
                    AND b.is_active = true
                    ORDER BY ec.name
                """, user_id_int)
            except ValueError:
                # user_id is not a number, treat as username
                rows = await conn.fetch("""
                    SELECT b.*, ec.name as category_name, ec.color as category_color
                    FROM core_budget b
                    JOIN core_expensecategory ec ON b.category_id = ec.id
                    JOIN auth_user u ON b.user_id = u.id
                    WHERE u.username = $1
                    AND b.is_active = true
                    ORDER BY ec.name
                """, user_id)
            
            return [dict(row) for row in rows]
    
    async def set_budget(self, user_id: str, category: str, monthly_limit: float, alert_threshold: float = 80.0) -> bool:
        """Set budget for category"""
        try:
            async with self.get_connection() as conn:
                category_id = await self._get_or_create_category(conn, category)
                
                await conn.execute("""
                    INSERT INTO core_budget (user_id, category_id, monthly_limit, alert_threshold)
                    VALUES ($1, $2, $3, $4)
                    ON CONFLICT (user_id, category_id) DO UPDATE SET
                        monthly_limit = EXCLUDED.monthly_limit,
                        alert_threshold = EXCLUDED.alert_threshold,
                        updated_at = NOW()
                """, user_id, category_id, monthly_limit, alert_threshold)
                
                return True
        except Exception as e:
            logger.error(f"Error setting budget: {e}")
            return False
    
    # AI Recommendations Methods
    async def save_ai_recommendation(self, user_id: str, recommendation_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Save AI-generated recommendation"""
        try:
            async with self.get_connection() as conn:
                row = await conn.fetchrow("""
                    INSERT INTO core_airecommendation (
                        user_id, recommendation_type, title, description,
                        priority, estimated_impact, estimated_savings
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                    RETURNING *
                """,
                user_id,
                recommendation_data['recommendation_type'],
                recommendation_data['title'],
                recommendation_data['description'],
                recommendation_data.get('priority', 'medium'),
                recommendation_data.get('estimated_impact', 'medium'),
                recommendation_data.get('estimated_savings')
                )
                
                return dict(row)
        except Exception as e:
            logger.error(f"Error saving AI recommendation: {e}")
            return None
    
    async def get_user_recommendations(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get user AI recommendations"""
        async with self.get_connection() as conn:
            # Try to convert user_id to int, if it fails, treat as username
            try:
                user_id_int = int(user_id)
                rows = await conn.fetch("""
                    SELECT *
                    FROM core_airecommendation
                    WHERE user_id = $1
                    AND is_dismissed = false
                    ORDER BY priority DESC, created_at DESC
                    LIMIT $2
                """, user_id_int, limit)
            except ValueError:
                # user_id is not a number, treat as username
                rows = await conn.fetch("""
                    SELECT *
                    FROM core_airecommendation
                    WHERE user_id = (SELECT id FROM auth_user WHERE username = $1)
                    AND is_dismissed = false
                    ORDER BY priority DESC, created_at DESC
                    LIMIT $2
                """, user_id, limit)
            
            return [dict(row) for row in rows]
    
    # Helper Methods
    async def _get_or_create_category(self, conn, category_name: str) -> str:
        """Get or create expense category"""
        # Try to get existing category
        category_id = await conn.fetchval(
            "SELECT id FROM core_expensecategory WHERE name = $1",
            category_name
        )
        
        if category_id:
            return category_id
        
        # Create new category
        category_id = await conn.fetchval("""
            INSERT INTO core_expensecategory (name, description)
            VALUES ($1, $2)
            RETURNING id
        """, category_name, f"Auto-created category: {category_name}")
        
        return category_id

    async def _resolve_user_id(self, conn, user_id_or_username: Union[str, int]) -> int:
        """Resolve provided user identifier to numeric auth_user.id.
        Accepts either an integer id or a username; raises if not found.
        """
        try:
            return int(user_id_or_username)
        except (ValueError, TypeError):
            resolved = await conn.fetchval(
                "SELECT id FROM auth_user WHERE username = $1",
                str(user_id_or_username)
            )
            if resolved is None:
                raise ValueError(f"User not found: {user_id_or_username}")
            return resolved

    def _normalize_expense_input(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Coerce inbound expense fields to DB-ready types and sane defaults."""
        # Amount -> Decimal
        amount = data.get('amount')
        if amount is None:
            raise ValueError('amount is required')
        if not isinstance(amount, Decimal):
            amount = Decimal(str(amount))

        # Date -> datetime
        raw_date = data.get('date')
        if raw_date is None:
            coerced_date = datetime.now()
        else:
            if isinstance(raw_date, datetime):
                coerced_date = raw_date
            elif isinstance(raw_date, date):
                coerced_date = datetime(raw_date.year, raw_date.month, raw_date.day)
            elif isinstance(raw_date, str):
                try:
                    # Try full ISO first, then date only
                    coerced_date = datetime.fromisoformat(raw_date)
                except ValueError:
                    # Fallback: treat as YYYY-MM-DD
                    parts = raw_date.split('T')[0].split('-')
                    if len(parts) == 3:
                        y, m, d = [int(p) for p in parts]
                        coerced_date = datetime(y, m, d)
                    else:
                        raise ValueError(f"Invalid date format: {raw_date}")
            else:
                raise ValueError("Unsupported date type")

        # Payment method normalization
        method = (data.get('payment_method') or 'credit_card').lower().strip()
        method_aliases = {
            'card': 'credit_card',
            'cc': 'credit_card',
            'debit': 'debit_card',
        }
        method = method_aliases.get(method, method)
        allowed_methods = {
            'credit_card', 'debit_card', 'cash', 'bank_transfer', 'digital_wallet', 'other'
        }
        if method not in allowed_methods:
            method = 'other'

        return {
            'amount': amount,
            'category': data.get('category', 'Other'),
            'description': data.get('description', ''),
            'merchant': data.get('merchant', ''),
            'payment_method': method,
            'date': coerced_date,
            'tags': data.get('tags', []) or [],
            'is_recurring': bool(data.get('is_recurring', False)),
            'recurring_frequency': data.get('recurring_frequency')
        }
    
    async def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        async with self.get_connection() as conn:
            stats = {}
            
            # Count records in each table
            tables = [
                'auth_user', 'core_userprofile', 'core_expense', 'core_expensecategory',
                'core_budget', 'core_investmentaccount', 'core_investment',
                'core_financialgoal', 'core_financialdata', 'core_airecommendation'
            ]
            
            for table in tables:
                try:
                    count = await conn.fetchval(f"SELECT COUNT(*) FROM {table}")
                    stats[table] = count
                except Exception as e:
                    stats[table] = f"Error: {e}"
            
            return stats

    async def get_expense_categories(self) -> List[Dict[str, Any]]:
        """List all expense categories"""
        async with self.get_connection() as conn:
            rows = await conn.fetch(
                "SELECT id, name, description, color, icon, is_active, created_at FROM core_expensecategory ORDER BY name"
            )
            return [dict(row) for row in rows]

# Global database manager instance
db_manager = DatabaseManager()
