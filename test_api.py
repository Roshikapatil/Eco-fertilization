"""
Test script for Crop Recommendation API
"""
import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:8000/api"

def test_api_status():
    """Test API status endpoint."""
    print("🔍 Testing API status...")
    try:
        response = requests.get(f"{BASE_URL}/status/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Status: {data['status']}")
            print(f"   Total recommendations: {data['total_recommendations']}")
            print(f"   Recent recommendations: {data['recent_recommendations']}")
            return True
        else:
            print(f"❌ API Status failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API Status error: {e}")
        return False

def test_recommendation():
    """Test crop recommendation endpoint."""
    print("\n🌱 Testing crop recommendation...")
    
    test_data = {
        "crop": "Rice",
        "season": "Monsoon",
        "soil": "Loamy",
        "preference": "Organic",
        "location_name": "Delhi",
        "latitude": 28.7041,
        "longitude": 77.1025
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/recommend/",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:
            data = response.json()
            print("✅ Recommendation created successfully!")
            print(f"   ID: {data['id']}")
            print(f"   Preferred technique: {data['preferred_technique']}")
            print(f"   Yield prediction: {data['yield_prediction']} kg/ha")
            print(f"   Location: {data['location_name']}")
            return data['id']
        else:
            print(f"❌ Recommendation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Recommendation error: {e}")
        return None

def test_recommendation_detail(recommendation_id):
    """Test getting specific recommendation details."""
    print(f"\n📋 Testing recommendation detail for ID {recommendation_id}...")
    
    try:
        response = requests.get(f"{BASE_URL}/recommend/{recommendation_id}/")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Recommendation detail retrieved!")
            print(f"   Crop: {data['crop']}")
            print(f"   Season: {data['season']}")
            print(f"   Soil: {data['soil']}")
            print(f"   Created: {data['created_at']}")
            return True
        else:
            print(f"❌ Recommendation detail failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Recommendation detail error: {e}")
        return False

def test_recommendation_history():
    """Test recommendation history endpoint."""
    print("\n📚 Testing recommendation history...")
    
    try:
        response = requests.get(f"{BASE_URL}/recommend/history/")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Recommendation history retrieved!")
            print(f"   Total count: {data['count']}")
            print(f"   Results: {len(data['results'])}")
            
            if data['results']:
                first_result = data['results'][0]
                print(f"   First result: {first_result['crop']} at {first_result['location_name']}")
            return True
        else:
            print(f"❌ Recommendation history failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Recommendation history error: {e}")
        return False

def test_filtering():
    """Test filtering functionality."""
    print("\n🔍 Testing filtering...")
    
    try:
        # Test crop filter
        response = requests.get(f"{BASE_URL}/recommend/history/?crop=Rice")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Filtering works!")
            print(f"   Filtered results: {len(data['results'])}")
            return True
        else:
            print(f"❌ Filtering failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Filtering error: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Starting Crop Recommendation API Tests")
    print("=" * 50)
    
    # Wait a moment for server to be ready
    time.sleep(2)
    
    # Test API status
    if not test_api_status():
        print("\n❌ API is not running. Please start the server first:")
        print("   python manage.py runserver")
        return
    
    # Test recommendation creation
    recommendation_id = test_recommendation()
    
    # Test recommendation detail
    if recommendation_id:
        test_recommendation_detail(recommendation_id)
    
    # Test history
    test_recommendation_history()
    
    # Test filtering
    test_filtering()
    
    print("\n" + "=" * 50)
    print("🎉 API tests completed!")
    print("\nNext steps:")
    print("1. Check the Django admin at http://localhost:8000/admin/")
    print("2. View API documentation at http://localhost:8000/api/")
    print("3. Test with your frontend application")

if __name__ == "__main__":
    main()
