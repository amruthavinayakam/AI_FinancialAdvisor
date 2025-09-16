#!/usr/bin/env python3
"""
Test the quick advice endpoint
"""

import requests
import json

def test_quick_advice():
    """Test the quick advice endpoint"""
    
    print("🧪 Testing Quick Financial Advice Endpoint...")
    
    try:
        # Test the quick advice endpoint
        url = "http://127.0.0.1:8001/api/v1/quick-advice"
        data = {"query": "What stocks should I invest in?"}
        
        print(f"📝 Query: {data['query']}")
        print(f"🌐 URL: {url}")
        print("⏳ Sending request...")
        
        response = requests.post(url, json=data, timeout=30)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Success!")
            print(f"🎯 Advice: {result.get('advice', 'No advice')}")
        else:
            print(f"❌ Error: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out - server might be slow")
    except requests.exceptions.ConnectionError:
        print("🔌 Connection error - is the server running?")
    except Exception as e:
        print(f"💥 Exception: {str(e)}")

if __name__ == "__main__":
    test_quick_advice()
