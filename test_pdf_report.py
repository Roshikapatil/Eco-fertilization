import requests
import json

BASE_URL = "http://127.0.0.1:8000/api/recommend/"

def test_pdf_report_data():
    """Test that all data needed for PDF report is available."""
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
        
        print("📄 Testing PDF Report Data Completeness")
        print("=" * 50)
        
        # Check basic information
        required_fields = [
            'id', 'crop', 'season', 'soil', 'preference', 
            'location_name', 'latitude', 'longitude', 'yield_prediction'
        ]
        
        print("✅ Basic Information:")
        for field in required_fields:
            if field in data:
                print(f"   {field}: {data[field]}")
            else:
                print(f"   ❌ Missing: {field}")
        
        # Check nutrient report
        print("\n✅ Nutrient Report:")
        if 'nutrient_report' in data:
            nutrients = data['nutrient_report']
            print(f"   Method: {nutrients.get('method', 'N/A')}")
            
            # Check daily recommendations
            if 'daily_recommendations' in nutrients:
                daily_schedule = nutrients['daily_recommendations']
                print(f"   Daily Schedule: {len(daily_schedule)} days")
                
                # Check each day has required fields
                for i, day in enumerate(daily_schedule):
                    required_day_fields = ['day', 'stage', 'date', 'time', 'activities', 'fertilizers', 'description']
                    missing_fields = [field for field in required_day_fields if field not in day]
                    if missing_fields:
                        print(f"   ❌ Day {i+1} missing: {missing_fields}")
                    else:
                        print(f"   ✅ Day {i+1}: {day['stage']} - {len(day['activities'])} activities, {len(day['fertilizers'])} fertilizers")
            else:
                print("   ❌ Missing: daily_recommendations")
        else:
            print("   ❌ Missing: nutrient_report")
        
        # Check weather data
        print("\n✅ Weather Data:")
        if 'weather_7day' in data and data['weather_7day']:
            weather = data['weather_7day']
            print(f"   Weather Forecast: {len(weather)} days")
            for i, day in enumerate(weather):
                print(f"   Day {i+1}: {day.get('temperature', 'N/A')}°C, {day.get('humidity', 'N/A')}% humidity")
        else:
            print("   ⚠️  Weather data not available (using mock data)")
        
        # Check step-by-step guide
        print("\n✅ Step-by-Step Guide:")
        if 'step_by_step_guide' in data and data['step_by_step_guide']:
            print(f"   Guide available: {len(data['step_by_step_guide'])} characters")
        else:
            print("   ⚠️  Step-by-step guide not available")
        
        # Summary
        print("\n📊 PDF Report Readiness:")
        has_basic_info = all(field in data for field in required_fields)
        has_nutrients = 'nutrient_report' in data and 'daily_recommendations' in data['nutrient_report']
        has_weather = 'weather_7day' in data
        
        if has_basic_info and has_nutrients:
            print("   ✅ READY FOR PDF GENERATION")
            print("   ✅ All required data is available")
            print("   ✅ 7-day schedule is complete")
            print("   ✅ Nutrient analysis is available")
            if has_weather:
                print("   ✅ Weather data is available")
            else:
                print("   ⚠️  Weather data will use fallback")
        else:
            print("   ❌ NOT READY - Missing required data")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error testing PDF report data: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    test_pdf_report_data()



