#!/usr/bin/env python3
"""
Test script to verify different farming preferences show correct details.
"""

import requests
import json

API_BASE = 'http://127.0.0.1:8000/api'

def test_farming_preference(preference):
    """Test a specific farming preference."""
    print(f"\n🌾 Testing {preference} Farming...")
    print("=" * 50)
    
    test_data = {
        'crop': 'Rice',
        'season': 'Kharif',
        'soil': 'Loamy',
        'preference': preference,
        'location_name': 'Delhi',
        'latitude': 28.6139,
        'longitude': 77.2090,
        'planting_date': '2025-09-25'
    }
    
    try:
        response = requests.post(f'{API_BASE}/recommend/', json=test_data)
        response.raise_for_status()
        
        data = response.json()
        nutrient_report = data.get('nutrient_report', {})
        
        print(f"✅ {preference} recommendation successful!")
        print(f"   Method: {nutrient_report.get('method', 'Unknown')}")
        
        # Check what details are shown based on preference
        if preference == 'Organic':
            if 'organic_details' in nutrient_report:
                organic = nutrient_report['organic_details']
                print(f"   🌿 Organic Details Found:")
                print(f"      - Total Organic Matter: {organic.get('total_organic_matter', 0)} kg/ha")
                print(f"      - Fertilizers: {len(organic.get('fertilizers', {}))} types")
                print(f"      - Practices: {len(organic.get('organic_practices', []))} practices")
                print(f"      - Benefits: {len(organic.get('benefits', []))} benefits")
            else:
                print("   ❌ No organic_details found!")
                
        elif preference == 'Inorganic':
            if 'npk_nutrients' in nutrient_report:
                npk = nutrient_report['npk_nutrients']
                print(f"   🧪 NPK Nutrients Found:")
                print(f"      - Nitrogen: {npk.get('nitrogen', {}).get('value', 0)} kg/ha")
                print(f"      - Phosphorus: {npk.get('phosphorus', {}).get('value', 0)} kg/ha")
                print(f"      - Potassium: {npk.get('potassium', {}).get('value', 0)} kg/ha")
                print(f"      - Total NPK: {npk.get('total_npk', 0)} kg/ha")
                print(f"      - Fertilizers: {len(npk.get('fertilizers', {}))} types")
            else:
                print("   ❌ No npk_nutrients found!")
                
        elif preference == 'Mixed':
            if 'mixed_details' in nutrient_report:
                mixed = nutrient_report['mixed_details']
                print(f"   🌿 Mixed Details Found:")
                print(f"      - Organic Ratio: {mixed.get('organic_ratio', 'Unknown')}")
                print(f"      - Inorganic Ratio: {mixed.get('inorganic_ratio', 'Unknown')}")
                print(f"      - Fertilizers: {len(mixed.get('fertilizers', {}))} combinations")
                print(f"      - Practices: {len(mixed.get('mixed_practices', []))} practices")
                print(f"      - Benefits: {len(mixed.get('benefits', []))} benefits")
            else:
                print("   ❌ No mixed_details found!")
        
        # Check if old base_nutrients is NOT present (should be replaced)
        if 'base_nutrients' in nutrient_report:
            print("   ⚠️  Warning: base_nutrients still present (should be replaced)")
        else:
            print("   ✅ base_nutrients correctly replaced with specific details")
            
        return True
        
    except Exception as e:
        print(f"❌ Error testing {preference}: {str(e)}")
        return False

def main():
    print("🌱 Farming Preference Test")
    print("=" * 50)
    
    preferences = ['Organic', 'Inorganic', 'Mixed']
    results = []
    
    for preference in preferences:
        success = test_farming_preference(preference)
        results.append((preference, success))
    
    print("\n📊 Test Results Summary:")
    print("=" * 50)
    for preference, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {preference}: {status}")
    
    all_passed = all(success for _, success in results)
    if all_passed:
        print("\n🎉 All tests passed! Farming preferences working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()






