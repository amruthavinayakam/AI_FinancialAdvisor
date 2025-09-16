#!/usr/bin/env python3
"""
Database setup script for Financial Advisor AI Agent
This script creates the database, runs migrations, and sets up initial data
"""

import os
import sys
import asyncio
import asyncpg
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.django_app.core.settings')

import django
django.setup()

from django.core.management import execute_from_command_line
from django.db import connection
from ai_core.database_manager import db_manager

async def create_database():
    """Create the database if it doesn't exist"""
    db_config = {
        'user': os.getenv('POSTGRES_USER', 'amrutha'),
        'password': os.getenv('POSTGRES_PASSWORD', 'vamru'),
        'host': os.getenv('POSTGRES_HOST', 'localhost'),
        'port': os.getenv('POSTGRES_PORT', '5432'),
        'database': 'postgres'  # Connect to default postgres db
    }
    
    try:
        conn = await asyncpg.connect(**db_config)
        
        # Check if our database exists
        db_name = os.getenv('POSTGRES_DB', 'project')
        exists = await conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1", db_name
        )
        
        if not exists:
            print(f"Creating database: {db_name}")
            await conn.execute(f'CREATE DATABASE "{db_name}"')
            print(f"✅ Database '{db_name}' created successfully")
        else:
            print(f"✅ Database '{db_name}' already exists")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        raise

async def setup_initial_data():
    """Set up initial data like expense categories"""
    try:
        await db_manager.initialize()
        
        # Create default expense categories
        categories = [
            {'name': 'Food & Dining', 'description': 'Restaurants, groceries, food delivery', 'color': '#e74c3c', 'icon': 'restaurant'},
            {'name': 'Transportation', 'description': 'Gas, public transit, rideshare, car maintenance', 'color': '#3498db', 'icon': 'car'},
            {'name': 'Shopping', 'description': 'Clothing, electronics, general merchandise', 'color': '#9b59b6', 'icon': 'shopping-bag'},
            {'name': 'Entertainment', 'description': 'Movies, games, subscriptions, hobbies', 'color': '#f39c12', 'icon': 'film'},
            {'name': 'Bills & Utilities', 'description': 'Electricity, water, internet, phone bills', 'color': '#2ecc71', 'icon': 'receipt'},
            {'name': 'Healthcare', 'description': 'Medical expenses, pharmacy, insurance', 'color': '#e67e22', 'icon': 'medical'},
            {'name': 'Education', 'description': 'Tuition, books, courses, training', 'color': '#1abc9c', 'icon': 'book'},
            {'name': 'Travel', 'description': 'Vacations, business trips, accommodation', 'color': '#34495e', 'icon': 'plane'},
            {'name': 'Insurance', 'description': 'Life, auto, home, health insurance', 'color': '#95a5a6', 'icon': 'shield'},
            {'name': 'Savings & Investments', 'description': 'Emergency fund, retirement, investments', 'color': '#27ae60', 'icon': 'trending-up'},
            {'name': 'Debt Payments', 'description': 'Credit cards, loans, mortgage payments', 'color': '#c0392b', 'icon': 'credit-card'},
            {'name': 'Other', 'description': 'Miscellaneous expenses', 'color': '#7f8c8d', 'icon': 'more-horizontal'}
        ]
        
        async with db_manager.get_connection() as conn:
            for category in categories:
                await conn.execute("""
                    INSERT INTO core_expensecategory (name, description, color, icon)
                    VALUES ($1, $2, $3, $4)
                    ON CONFLICT (name) DO NOTHING
                """, category['name'], category['description'], category['color'], category['icon'])
        
        print("✅ Initial expense categories created")
        
        # Create a sample user profile if none exists
        async with db_manager.get_connection() as conn:
            # Check if any users exist
            user_count = await conn.fetchval("SELECT COUNT(*) FROM auth_user")
            
            if user_count == 0:
                print("Creating sample user...")
                # Create a sample user
                user_id = await conn.fetchval("""
                    INSERT INTO auth_user (username, email, first_name, last_name, is_staff, is_active, date_joined)
                    VALUES ($1, $2, $3, $4, $5, $6, NOW())
                    RETURNING id
                """, 'demo_user', 'demo@example.com', 'Demo', 'User', True, True)
                
                # Create user profile
                await conn.execute("""
                    INSERT INTO core_userprofile (
                        user_id, monthly_income, monthly_budget, target_daily_spending,
                        savings_goal, risk_tolerance, investment_horizon, age
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                """, user_id, 5000, 3000, 100, 500, 'moderate', 'long_term', 30)
                
                print("✅ Sample user created: demo_user")
        
        await db_manager.close()
        
    except Exception as e:
        print(f"❌ Error setting up initial data: {e}")
        raise

def run_django_migrations():
    """Run Django migrations"""
    try:
        print("Running Django migrations...")
        
        # Make migrations
        execute_from_command_line(['manage.py', 'makemigrations', 'core'])
        print("✅ Django migrations created")
        
        # Apply migrations
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ Django migrations applied")
        
    except Exception as e:
        print(f"❌ Error running migrations: {e}")
        raise

async def main():
    """Main setup function"""
    print("🚀 Setting up Financial Advisor AI Agent Database...")
    print("=" * 60)
    
    try:
        # Step 1: Create database
        print("\n1. Creating database...")
        await create_database()
        
        # Step 2: Run Django migrations
        print("\n2. Running Django migrations...")
        run_django_migrations()
        
        # Step 3: Set up initial data
        print("\n3. Setting up initial data...")
        await setup_initial_data()
        
        print("\n" + "=" * 60)
        print("✅ Database setup completed successfully!")
        print("\nNext steps:")
        print("1. Start the FastAPI server: python -m backend.fastapi_app.main")
        print("2. Start the Django server: python backend/django_app/manage.py runserver")
        print("3. Access Django admin at: http://localhost:8000/admin/")
        print("4. Access FastAPI docs at: http://localhost:8001/docs")
        
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
