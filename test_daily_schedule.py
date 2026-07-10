import requests
import json

BASE_URL = "http://127.0.0.1:8000/api/recommend/"

def test_daily_schedule():
    """Test the new 7-day detailed process schedule."""
    payload = {
        "crop": "Rice",
        "season": "Kharif",
        "soil": "Loamy",
        "preference": "Organic",
        "location_name": "Delhi",
        "latitude": 28.6139,
        "longitude": 77.2090,
        "planting_date": "2025-10-11"
    }
    
    try:
        response = requests.post(BASE_URL, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        print("🌱 Testing 7-Day Detailed Process Schedule")
        print("=" * 50)
        
        if 'nutrient_report' in data and 'daily_recommendations' in data['nutrient_report']:
            daily_schedule = data['nutrient_report']['daily_recommendations']
            
            print(f"✅ Daily schedule found with {len(daily_schedule)} days")
            print()
            
            for day in daily_schedule:
                print(f"📅 Day {day['day']} - {day['stage']}")
                print(f"   Date: {day['date']}")
                print(f"   Time: {day['time']}")
                print(f"   Activities: {', '.join(day['activities'])}")
                print(f"   Description: {day['description']}")
                
                if day['fertilizers']:
                    print("   Fertilizers:")
                    for fertilizer in day['fertilizers']:
                        print(f"     - {fertilizer['type']}: {fertilizer['quantity']} kg/ha")
                        print(f"       Application: {fertilizer['application']}")
                else:
                    print("   Fertilizers: No specific applications")
                print()
            
            # Check if we have varied content (not all the same)
            stages = [day['stage'] for day in daily_schedule]
            unique_stages = set(stages)
            
            if len(unique_stages) > 1:
                print("✅ SUCCESS: Daily schedule shows varied stages and processes!")
                print(f"   Found {len(unique_stages)} unique stages: {', '.join(unique_stages)}")
            else:
                print("❌ WARNING: All days show the same stage")
                
            # Check for fertilizer applications
            days_with_fertilizers = sum(1 for day in daily_schedule if day['fertilizers'])
            print(f"📊 Days with fertilizer applications: {days_with_fertilizers}/7")
            
        else:
            print("❌ No daily recommendations found in response")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error testing daily schedule: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    test_daily_schedule()



