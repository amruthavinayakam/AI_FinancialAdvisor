#!/usr/bin/env python3
"""
Test the simple advice endpoint
"""

import requests
import json

def test_simple_advice():
    """Test the simple advice endpoint"""
    
    print("🧪 Testing Simple Financial Advice Endpoint...")
    
    try:
        # Test the simple advice endpoint
        url = "http://127.0.0.1:8001/api/v1/simple-advice"
        data = {"query": "What stocks should I invest in?"}
        
        print(f"📝 Query: {data['query']}")
        print(f"🌐 URL: {url}")
        print("⏳ Sending request...")
        
        response = requests.post(url, json=data, timeout=10)
        
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
    test_simple_advice()
