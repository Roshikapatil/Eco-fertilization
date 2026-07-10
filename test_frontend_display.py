#!/usr/bin/env python3
"""
Test script to verify frontend displays correct content based on farming preference.
"""

import requests
import json

API_BASE = 'http://127.0.0.1:8000/api'

def test_frontend_display():
    """Test that the API returns the correct structure for frontend display."""
    print("🌱 Frontend Display Test")
    print("=" * 50)
    
    preferences = ['Organic', 'Inorganic', 'Mixed']
    
    for preference in preferences:
        print(f"\n🌾 Testing {preference} Frontend Display...")
        print("-" * 30)
        
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
            
            print(f"✅ {preference} API Response:")
            print(f"   Method: {nutrient_report.get('method', 'Unknown')}")
            
            # Check what the frontend will display
            if preference == 'Organic':
                if 'organic_details' in nutrient_report:
                    organic = nutrient_report['organic_details']
                    print(f"   🌿 Frontend will show:")
                    print(f"      - Organic Farming Details section")
                    print(f"      - Total Organic Matter: {organic.get('total_organic_matter', 0)} kg/ha")
                    print(f"      - {len(organic.get('fertilizers', {}))} organic fertilizers")
                    print(f"      - {len(organic.get('organic_practices', []))} organic practices")
                    print(f"      - {len(organic.get('benefits', []))} benefits")
                else:
                    print("   ❌ Missing organic_details for frontend")
                    
            elif preference == 'Inorganic':
                if 'npk_nutrients' in nutrient_report:
                    npk = nutrient_report['npk_nutrients']
                    print(f"   🧪 Frontend will show:")
                    print(f"      - NPK Nutrients section")
                    print(f"      - Nitrogen: {npk.get('nitrogen', {}).get('value', 0)} kg/ha")
                    print(f"      - Phosphorus: {npk.get('phosphorus', {}).get('value', 0)} kg/ha")
                    print(f"      - Potassium: {npk.get('potassium', {}).get('value', 0)} kg/ha")
                    print(f"      - {len(npk.get('fertilizers', {}))} chemical fertilizers")
                else:
                    print("   ❌ Missing npk_nutrients for frontend")
                    
            elif preference == 'Mixed':
                if 'mixed_details' in nutrient_report:
                    mixed = nutrient_report['mixed_details']
                    print(f"   🌿 Frontend will show:")
                    print(f"      - Mixed Farming Details section")
                    print(f"      - Organic Ratio: {mixed.get('organic_ratio', 'Unknown')}")
                    print(f"      - Inorganic Ratio: {mixed.get('inorganic_ratio', 'Unknown')}")
                    print(f"      - {len(mixed.get('fertilizers', {}))} mixed combinations")
                    print(f"      - {len(mixed.get('mixed_practices', []))} mixed practices")
                else:
                    print("   ❌ Missing mixed_details for frontend")
            
            # Check if old structure is gone
            if 'base_nutrients' in nutrient_report:
                print("   ⚠️  Warning: base_nutrients still present (frontend might show old format)")
            else:
                print("   ✅ base_nutrients correctly removed (frontend will show new format)")
                
        except Exception as e:
            print(f"❌ Error testing {preference}: {str(e)}")
    
    print("\n🎯 Frontend Display Test Complete!")
    print("=" * 50)
    print("The frontend should now display:")
    print("• Organic → Organic farming details (compost, manure, practices)")
    print("• Inorganic → NPK nutrients details (chemical fertilizers)")
    print("• Mixed → Mixed farming details (combinations, ratios)")

if __name__ == "__main__":
    test_frontend_display()






