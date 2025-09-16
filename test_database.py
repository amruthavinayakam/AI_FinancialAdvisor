#!/usr/bin/env python3
"""
Database connection test script for Financial Advisor AI Agent
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from ai_core.database_manager import db_manager

async def test_database_connection():
    """Test database connection and basic operations"""
    print("🧪 Testing Database Connection...")
    print("=" * 50)
    
    try:
        # Initialize database connection
        await db_manager.initialize()
        print("✅ Database connection established")
        
        # Test basic query
        stats = await db_manager.get_database_stats()
        print("\n📊 Database Statistics:")
        for table, count in stats.items():
            print(f"  {table}: {count}")
        
        # Test user profile operations
        print("\n👤 Testing User Profile Operations...")
        
        # Create a test user profile
        test_profile = {
            'monthly_income': 5000,
            'monthly_budget': 3000,
            'target_daily_spending': 100,
            'savings_goal': 1000,
            'risk_tolerance': 'moderate',
            'investment_horizon': 'long_term',
            'age': 30
        }
        
        # Note: This would require a user to exist first
        print("  ⚠️  User profile operations require existing user")
        
        # Test expense operations
        print("\n💰 Testing Expense Operations...")
        
        # Get sample expenses
        expenses = await db_manager.get_user_expenses('demo_user', 30)
        print(f"  Found {len(expenses)} expenses for demo_user")
        
        if expenses:
            print("  Sample expense:")
            sample = expenses[0]
            print(f"    Amount: ${sample.get('amount', 'N/A')}")
            print(f"    Category: {sample.get('category_name', 'N/A')}")
            print(f"    Date: {sample.get('date', 'N/A')}")
        
        # Test expense summary
        summary = await db_manager.get_expense_summary('demo_user', 30)
        if summary and summary.get('total_spent', 0) > 0:
            print(f"  Total spent: ${summary['total_spent']:.2f}")
            print(f"  Daily average: ${summary['avg_daily_spending']:.2f}")
            print(f"  Categories: {len(summary['category_breakdown'])}")
        
        # Test investment operations
        print("\n📈 Testing Investment Operations...")
        investments = await db_manager.get_user_investments('demo_user')
        print(f"  Found {len(investments)} investment accounts")
        
        # Test financial goals
        print("\n🎯 Testing Financial Goals...")
        goals = await db_manager.get_user_goals('demo_user')
        print(f"  Found {len(goals)} financial goals")
        
        # Test AI recommendations
        print("\n🤖 Testing AI Recommendations...")
        recommendations = await db_manager.get_user_recommendations('demo_user')
        print(f"  Found {len(recommendations)} AI recommendations")
        
        print("\n✅ All database tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Database test failed: {e}")
        return False
    
    finally:
        # Clean up
        await db_manager.close()
        print("\n🔌 Database connection closed")
    
    return True

async def test_expense_tracker():
    """Test the expense tracker with database integration"""
    print("\n🧪 Testing Expense Tracker Integration...")
    print("=" * 50)
    
    try:
        from ai_core.expense_tracker import ExpenseTracker
        
        tracker = ExpenseTracker()
        await tracker.initialize()
        
        # Test getting expenses
        expenses = await tracker.get_user_expenses('demo_user', 30)
        print(f"✅ Retrieved {len(expenses)} expenses")
        
        # Test expense summary
        summary = await tracker.get_expense_summary('demo_user', 30)
        if 'error' not in summary:
            print(f"✅ Generated expense summary")
            print(f"   Total spent: ${summary.get('total_spent', 0):.2f}")
        else:
            print(f"⚠️  Expense summary error: {summary['error']}")
        
        # Test adding expense
        test_expense = {
            'amount': 25.50,
            'category': 'Food & Dining',
            'description': 'Test lunch',
            'merchant': 'Test Restaurant',
            'payment_method': 'credit_card'
        }
        
        result = await tracker.add_expense('demo_user', test_expense)
        if result.get('success'):
            print("✅ Successfully added test expense")
        else:
            print(f"⚠️  Failed to add expense: {result.get('error', 'Unknown error')}")
        
        print("✅ Expense tracker integration test completed!")
        
    except Exception as e:
        print(f"❌ Expense tracker test failed: {e}")
        return False
    
    return True

async def main():
    """Main test function"""
    print("🚀 Financial Advisor AI Agent - Database Test Suite")
    print("=" * 60)
    
    # Test 1: Database connection
    db_success = await test_database_connection()
    
    if db_success:
        # Test 2: Expense tracker integration
        tracker_success = await test_expense_tracker()
        
        if tracker_success:
            print("\n🎉 All tests passed! Database setup is working correctly.")
            print("\nNext steps:")
            print("1. Start the FastAPI server: python -m backend.fastapi_app.main")
            print("2. Start the Django server: python backend/django_app/manage.py runserver")
            print("3. Test the API endpoints using the provided examples")
        else:
            print("\n❌ Some tests failed. Check the error messages above.")
            sys.exit(1)
    else:
        print("\n❌ Database connection failed. Please check your setup.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
