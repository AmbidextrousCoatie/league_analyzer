#!/usr/bin/env python3
"""
Debug script to test database parameter flow on remote server
"""

import requests
import json

def test_endpoint(base_url, endpoint, params=None):
    """Test an endpoint and return the response"""
    url = f"{base_url}{endpoint}"
    print(f"\n🔄 Testing: {url}")
    if params:
        print(f"📋 Parameters: {params}")
    
    try:
        response = requests.get(url, params=params)
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Response: {json.dumps(data, indent=2)[:500]}...")
            return data
        else:
            print(f"❌ Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return None

def main():
    # Replace with your remote server URL
    base_url = "http://your-remote-server.com"  # Change this to your actual remote server URL
    
    print("🔍 Debugging Remote Server Database Parameter Flow")
    print("=" * 60)
    
    # Test 1: Check if the server is reachable
    print("\n1️⃣ Testing server connectivity...")
    try:
        response = requests.get(f"{base_url}/")
        print(f"✅ Server reachable: {response.status_code}")
    except Exception as e:
        print(f"❌ Server not reachable: {str(e)}")
        return
    
    # Test 2: Test database parameter with available seasons
    print("\n2️⃣ Testing available seasons with database parameter...")
    test_endpoint(base_url, "/league/get_available_seasons", {
        "database": "bowling_ergebnisse_real.csv"
    })
    
    # Test 3: Test available leagues with database parameter
    print("\n3️⃣ Testing available leagues with database parameter...")
    test_endpoint(base_url, "/league/get_available_leagues", {
        "database": "bowling_ergebnisse_real.csv",
        "season": "24/25"
    })
    
    # Test 4: Test individual averages with database parameter
    print("\n4️⃣ Testing individual averages with database parameter...")
    test_endpoint(base_url, "/league/get_individual_averages", {
        "database": "bowling_ergebnisse_real.csv",
        "league": "BayL",
        "season": "24/25",
        "week": "6"
    })
    
    # Test 5: Test honor scores with database parameter
    print("\n5️⃣ Testing honor scores with database parameter...")
    test_endpoint(base_url, "/league/get_honor_scores", {
        "database": "bowling_ergebnisse_real.csv",
        "league": "BayL",
        "season": "24/25",
        "week": "6"
    })
    
    # Test 6: Test league week table with database parameter
    print("\n6️⃣ Testing league week table with database parameter...")
    test_endpoint(base_url, "/league/get_league_week_table", {
        "database": "bowling_ergebnisse_real.csv",
        "league": "BayL",
        "season": "24/25",
        "week": "6"
    })
    
    # Test 7: Test latest events with database parameter
    print("\n7️⃣ Testing latest events with database parameter...")
    test_endpoint(base_url, "/get_latest_events", {
        "database": "bowling_ergebnisse_real.csv"
    })
    
    # Test 8: Test the new filter endpoints test
    print("\n8️⃣ Testing filter endpoints test...")
    test_endpoint(base_url, "/test-filter-endpoints", {
        "database": "bowling_ergebnisse_real.csv",
        "season": "24/25",
        "league": "BayL"
    })
    
    print("\n" + "=" * 60)
    print("🏁 Debug testing complete!")

if __name__ == "__main__":
    main()
