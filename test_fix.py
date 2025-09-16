#!/usr/bin/env python3
"""
Test script to verify the financial advisor fix
"""

import asyncio
import sys
import os

# Add the ai_core module to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'ai_core'))

from ai_core.financial_advisor_graph import FinancialAdvisorGraph

async def test_financial_advice():
    """Test the financial advice endpoint with a simple query"""
    
    print("🧪 Testing Financial Advisor Fix...")
    
    try:
        # Initialize the financial advisor
        advisor = FinancialAdvisorGraph()
        
        # Test with a simple query
        query = "What stocks should I invest in?"
        user_id = "test_user_123"
        
        print(f"📝 Query: {query}")
        print(f"👤 User ID: {user_id}")
        print("⏳ Processing...")
        
        # Get financial advice
        result = await advisor.get_financial_advice(query, user_id)
        
        print("\n✅ Result:")
        print(f"Success: {result.get('success', False)}")
        
        if result.get('success'):
            print("🎉 Financial advice generated successfully!")
            print(f"📊 Advice: {result.get('advice', 'No advice generated')[:200]}...")
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"💥 Exception occurred: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_financial_advice())
