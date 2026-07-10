#!/usr/bin/env python3
"""
Example script to test the crop recommendation API.
This demonstrates how to properly make POST requests to the API.
"""

import requests
import json

# API base URL
BASE_URL = "http://127.0.0.1:8000"

def test_api_status():
    """Test the API status endpoint (GET request)"""
    print("Testing API Status...")
    try:
        response = requests.get(f"{BASE_URL}/api/status/")
        if response.status_code == 200:
            print("✅ API Status:", response.json())
        else:
            print("❌ API Status failed:", response.status_code)
    except Exception as e:
        print("❌ Error:", str(e))

def test_crop_recommendation():
    """Test the crop recommendation endpoint (POST request)"""
    print("\nTesting Crop Recommendation...")
    
    # Sample data for crop recommendation
    sample_data = {
        "crop": "Rice",
        "season": "Kharif",
        "soil": "Loamy",
        "preference": "Organic",
        "location_name": "Delhi",
        "latitude": 28.6139,
        "longitude": 77.2090
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/recommend/",
            json=sample_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 201:
            print("✅ Crop Recommendation successful!")
            result = response.json()
            print(f"   Recommendation ID: {result.get('id')}")
            print(f"   Crop: {result.get('crop')}")
            print(f"   Location: {result.get('location_name')}")
            print(f"   Preferred Technique: {result.get('preferred_technique')}")
            print(f"   Yield Prediction: {result.get('yield_prediction')}")
        else:
            print(f"❌ Crop Recommendation failed: {response.status_code}")
            print("   Response:", response.text)
    except Exception as e:
        print("❌ Error:", str(e))

def test_recommendation_history():
    """Test the recommendation history endpoint (GET request)"""
    print("\nTesting Recommendation History...")
    try:
        response = requests.get(f"{BASE_URL}/api/recommend/history/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Found {data.get('count', 0)} recommendations")
            if data.get('results'):
                print("   Recent recommendations:")
                for rec in data['results'][:3]:  # Show first 3
                    print(f"   - {rec['crop']} at {rec['location_name']} ({rec['created_at']})")
        else:
            print("❌ History failed:", response.status_code)
    except Exception as e:
        print("❌ Error:", str(e))

if __name__ == "__main__":
    print("🌱 Crop Recommendation API Test")
    print("=" * 40)
    
    # Test all endpoints
    test_api_status()
    test_crop_recommendation()
    test_recommendation_history()
    
    print("\n" + "=" * 40)
    print("Test completed!")
    print("\nTo test manually:")
    print("1. API Status: GET http://127.0.0.1:8000/api/status/")
    print("2. Crop Recommendation: POST http://127.0.0.1:8000/api/recommend/")
    print("3. History: GET http://127.0.0.1:8000/api/recommend/history/")
    print("\nFor POST requests, use tools like Postman, curl, or this script.")


