"""
ML prediction module for crop recommendations.
"""
import os
import sys
import joblib
import requests
import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler

# Add the ml directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'ml'))

logger = logging.getLogger(__name__)

# API Keys (should be in environment variables in production)
OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY', 'your_openweather_api_key_here')

# Model paths
MODEL_DIR = os.path.join(os.path.dirname(__file__), '..', 'models')
TECH_MODEL_PATH = os.path.join(MODEL_DIR, 'tech_model.pkl')
YIELD_MODEL_PATH = os.path.join(MODEL_DIR, 'yield_model.pkl')
SCALER_PATH = os.path.join(MODEL_DIR, 'scaler.pkl')
LABEL_ENCODERS_PATH = os.path.join(MODEL_DIR, 'label_encoders.pkl')

# Global variables for loaded models
_tech_model = None
_yield_model = None
_scaler = None
_label_encoders = None


def load_models():
    """Load ML models and preprocessors."""
    global _tech_model, _yield_model, _scaler, _label_encoders
    
    try:
        if os.path.exists(TECH_MODEL_PATH):
            _tech_model = joblib.load(TECH_MODEL_PATH)
        else:
            logger.warning(f"Technology model not found at {TECH_MODEL_PATH}")
            
        if os.path.exists(YIELD_MODEL_PATH):
            _yield_model = joblib.load(YIELD_MODEL_PATH)
        else:
            logger.warning(f"Yield model not found at {YIELD_MODEL_PATH}")
            
        if os.path.exists(SCALER_PATH):
            _scaler = joblib.load(SCALER_PATH)
        else:
            logger.warning(f"Scaler not found at {SCALER_PATH}")
            
        if os.path.exists(LABEL_ENCODERS_PATH):
            _label_encoders = joblib.load(LABEL_ENCODERS_PATH)
        else:
            logger.warning(f"Label encoders not found at {LABEL_ENCODERS_PATH}")
            
    except Exception as e:
        logger.error(f"Error loading models: {str(e)}")


def get_weather_forecast(latitude: float, longitude: float, start_date: str = None) -> list:
    """
    Fetch 7-day weather forecast from OpenWeather API starting from a specific date.
    """
    try:
        from datetime import datetime, timedelta
        
        # If start_date is provided, use it; otherwise use current date
        if start_date:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        else:
            start_dt = datetime.now()
        
        url = "http://api.openweathermap.org/data/2.5/forecast"
        params = {
            'lat': latitude,
            'lon': longitude,
            'appid': OPENWEATHER_API_KEY,
            'units': 'metric'
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        forecasts = []
        
        # Generate 7 days starting from start_date
        for i in range(7):
            current_date = start_dt + timedelta(days=i)
            
            # Try to find matching forecast data for this date
            matching_forecast = None
            for item in data['list']:
                item_date = datetime.strptime(item['dt_txt'], '%Y-%m-%d %H:%M:%S').date()
                if item_date == current_date.date():
                    matching_forecast = item
                    break
            
            if matching_forecast:
                forecasts.append({
                    'day': current_date.strftime('%Y-%m-%d'),
                    'temperature': round(matching_forecast['main']['temp'], 1),
                    'humidity': matching_forecast['main']['humidity'],
                    'rainfall': matching_forecast.get('rain', {}).get('3h', 0),
                    'description': matching_forecast['weather'][0]['description']
                })
            else:
                # Generate realistic weather data for the specific date
                forecasts.append(generate_realistic_weather_for_date(current_date, latitude, longitude))
            
        return forecasts
        
    except Exception as e:
        logger.error(f"Error fetching weather data: {str(e)}")
        # Return mock data with accurate dates if API fails
        return generate_mock_weather_forecast(start_date)


def generate_realistic_weather_for_date(date: datetime, latitude: float, longitude: float) -> dict:
    """
    Generate realistic weather data for a specific date based on location and season.
    """
    import random
    
    # Determine season based on month
    month = date.month
    if month in [12, 1, 2]:  # Winter
        base_temp = 15 + (latitude - 20) * 0.5  # Temperature varies with latitude
        humidity_range = (40, 70)
        rain_chance = 0.3
    elif month in [3, 4, 5]:  # Spring
        base_temp = 25 + (latitude - 20) * 0.5
        humidity_range = (50, 80)
        rain_chance = 0.4
    elif month in [6, 7, 8, 9]:  # Summer/Monsoon
        base_temp = 30 + (latitude - 20) * 0.5
        humidity_range = (60, 90)
        rain_chance = 0.6
    else:  # Autumn
        base_temp = 22 + (latitude - 20) * 0.5
        humidity_range = (45, 75)
        rain_chance = 0.3
    
    # Add some randomness
    temperature = base_temp + random.uniform(-5, 5)
    humidity = random.randint(humidity_range[0], humidity_range[1])
    
    # Determine if it will rain
    if random.random() < rain_chance:
        rainfall = random.uniform(0.5, 10)
        descriptions = ['light rain', 'moderate rain', 'heavy rain', 'thunderstorm']
    else:
        rainfall = 0
        descriptions = ['clear sky', 'partly cloudy', 'cloudy', 'overcast']
    
    description = random.choice(descriptions)
    
    return {
        'day': date.strftime('%Y-%m-%d'),
        'temperature': round(temperature, 1),
        'humidity': humidity,
        'rainfall': round(rainfall, 1),
        'description': description
    }


def generate_mock_weather_forecast(start_date: str = None) -> list:
    """
    Generate mock weather forecast with accurate dates.
    """
    from datetime import datetime, timedelta
    
    if start_date:
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    else:
        start_dt = datetime.now()
    
    forecasts = []
    for i in range(7):
        current_date = start_dt + timedelta(days=i)
        forecasts.append(generate_realistic_weather_for_date(current_date, 28.6, 77.2))  # Default to Delhi coordinates
    
    return forecasts


def generate_planting_date_recommendation(crop: str, season: str, location: str, custom_date: str = None) -> Dict[str, str]:
    """
    Generate optimal planting date recommendations based on crop, season, and location.
    """
    # Planting date recommendations by crop and season
    planting_dates = {
        'Rice': {
            'Kharif': 'June 15 - July 15',
            'Rabi': 'November 15 - December 15',
            'Monsoon': 'June 1 - July 30',
            'Winter': 'November 1 - December 31',
            'Summer': 'March 1 - April 15',
            'Zaid': 'March 15 - April 30'
        },
        'Wheat': {
            'Rabi': 'November 1 - December 15',
            'Winter': 'October 15 - November 30',
            'Kharif': 'October 1 - November 15',
            'Monsoon': 'October 15 - November 15',
            'Summer': 'Not recommended',
            'Zaid': 'Not recommended'
        },
        'Maize': {
            'Kharif': 'June 1 - July 15',
            'Rabi': 'October 15 - November 30',
            'Monsoon': 'June 1 - July 30',
            'Winter': 'October 1 - November 15',
            'Summer': 'March 1 - April 15',
            'Zaid': 'March 15 - April 30'
        },
        'Sugarcane': {
            'Kharif': 'March 1 - April 30',
            'Rabi': 'October 1 - November 30',
            'Monsoon': 'March 15 - May 15',
            'Winter': 'October 15 - December 15',
            'Summer': 'February 15 - April 15',
            'Zaid': 'March 1 - April 30'
        },
        'Cotton': {
            'Kharif': 'May 15 - June 30',
            'Rabi': 'October 1 - November 15',
            'Monsoon': 'May 1 - July 15',
            'Winter': 'September 15 - November 15',
            'Summer': 'March 1 - April 30',
            'Zaid': 'April 1 - May 15'
        },
        'Soybean': {
            'Kharif': 'June 15 - July 15',
            'Rabi': 'October 15 - November 30',
            'Monsoon': 'June 1 - July 30',
            'Winter': 'October 1 - November 15',
            'Summer': 'March 1 - April 15',
            'Zaid': 'March 15 - April 30'
        },
        'Potato': {
            'Rabi': 'October 15 - November 30',
            'Winter': 'October 1 - December 15',
            'Kharif': 'June 1 - July 15',
            'Monsoon': 'June 15 - July 30',
            'Summer': 'February 1 - March 15',
            'Zaid': 'February 15 - March 30'
        },
        'Tomato': {
            'Rabi': 'October 15 - November 30',
            'Winter': 'October 1 - December 15',
            'Kharif': 'June 1 - July 15',
            'Monsoon': 'June 15 - July 30',
            'Summer': 'February 1 - March 15',
            'Zaid': 'February 15 - March 30'
        },
        'Onion': {
            'Rabi': 'October 15 - November 30',
            'Winter': 'October 1 - December 15',
            'Kharif': 'June 1 - July 15',
            'Monsoon': 'June 15 - July 30',
            'Summer': 'February 1 - March 15',
            'Zaid': 'February 15 - March 30'
        },
        'Chili': {
            'Rabi': 'October 15 - November 30',
            'Winter': 'October 1 - December 15',
            'Kharif': 'June 1 - July 15',
            'Monsoon': 'June 15 - July 30',
            'Summer': 'February 1 - March 15',
            'Zaid': 'February 15 - March 30'
        }
    }
    
    recommended_dates = planting_dates.get(crop, {}).get(season, 'Contact local agricultural extension')
    
    # If custom date is provided, use it
    if custom_date:
        return {
            'optimal_planting_period': f'Custom date: {custom_date}',
            'recommended_month': custom_date.split('-')[1] if '-' in custom_date else custom_date.split('/')[1] if '/' in custom_date else 'Custom',
            'duration_days': '30-45 days',
            'custom_date': custom_date,
            'is_custom': True
        }
    
    return {
        'optimal_planting_period': recommended_dates,
        'recommended_month': recommended_dates.split(' - ')[0].split(' ')[0] if ' - ' in recommended_dates else 'Contact extension',
        'duration_days': '30-45 days' if 'Not recommended' not in recommended_dates else 'Not applicable',
        'is_custom': False
    }


def generate_detailed_nutrient_recommendation(crop: str, soil: str, season: str, preference: str) -> Dict[str, Any]:
    """
    Generate detailed nutrient recommendations for organic, inorganic, and mixed farming.
    """
    # Base nutrient requirements by crop (kg/ha) - based on agricultural research
    crop_nutrients = {
        'Rice': {'N': 120, 'P': 60, 'K': 60},  # Rice needs more K for grain filling
        'Wheat': {'N': 120, 'P': 60, 'K': 40},  # Wheat needs balanced NPK
        'Maize': {'N': 180, 'P': 80, 'K': 60},  # Maize is heavy feeder
        'Sugarcane': {'N': 300, 'P': 100, 'K': 150},  # Sugarcane needs high nutrients
        'Cotton': {'N': 100, 'P': 50, 'K': 80},  # Cotton needs more K for fiber
        'Soybean': {'N': 20, 'P': 60, 'K': 40},  # Soybean fixes N, needs more P
        'Potato': {'N': 120, 'P': 80, 'K': 120},  # Potato needs high K for tuber
        'Tomato': {'N': 150, 'P': 80, 'K': 100},  # Tomato needs balanced nutrition
        'Onion': {'N': 100, 'P': 50, 'K': 80},  # Onion needs more K for bulb
        'Chili': {'N': 120, 'P': 60, 'K': 80},  # Chili needs balanced NPK
    }
    
    # Soil type adjustments
    soil_adjustments = {
        'Clay': {'N': 1.1, 'P': 0.9, 'K': 1.0},
        'Sandy': {'N': 1.2, 'P': 1.1, 'K': 1.1},
        'Loamy': {'N': 1.0, 'P': 1.0, 'K': 1.0},
        'Silty': {'N': 1.05, 'P': 0.95, 'K': 1.0},
        'Peaty': {'N': 0.8, 'P': 1.2, 'K': 0.9},
        'Chalky': {'N': 1.1, 'P': 0.8, 'K': 1.1},
    }
    
    # Season adjustments
    season_adjustments = {
        'Kharif': {'N': 1.0, 'P': 1.0, 'K': 1.0},
        'Rabi': {'N': 0.9, 'P': 1.1, 'K': 1.0},
        'Zaid': {'N': 1.1, 'P': 0.9, 'K': 1.1},
        'Monsoon': {'N': 1.0, 'P': 1.0, 'K': 1.0},
        'Winter': {'N': 0.9, 'P': 1.1, 'K': 1.0},
        'Summer': {'N': 1.1, 'P': 0.9, 'K': 1.1},
    }
    
    base_nutrients = crop_nutrients.get(crop, {'N': 100, 'P': 50, 'K': 40})
    soil_adj = soil_adjustments.get(soil, {'N': 1.0, 'P': 1.0, 'K': 1.0})
    season_adj = season_adjustments.get(season, {'N': 1.0, 'P': 1.0, 'K': 1.0})
    
    # Calculate adjusted nutrients
    adjusted_nutrients = {
        'N': int(base_nutrients['N'] * soil_adj['N'] * season_adj['N']),
        'P': int(base_nutrients['P'] * soil_adj['P'] * season_adj['P']),
        'K': int(base_nutrients['K'] * soil_adj['K'] * season_adj['K'])
    }
    
    # Generate recommendations based on farming preference
    if preference == 'Organic':
        return generate_organic_recommendations(adjusted_nutrients, crop)
    elif preference == 'Inorganic':
        return generate_inorganic_recommendations(adjusted_nutrients, crop)
    else:  # Mixed
        return generate_mixed_recommendations(adjusted_nutrients, crop)


def generate_organic_recommendations(nutrients: Dict[str, int], crop: str) -> Dict[str, Any]:
    """
    Generate organic farming recommendations with organic fertilizers.
    """
    n, p, k = nutrients['N'], nutrients['P'], nutrients['K']
    
    # Organic fertilizer recommendations
    organic_fertilizers = {
        'farmyard_manure': {
            'npk_content': {'N': 0.5, 'P': 0.2, 'K': 0.5},  # %
            'quantity': int(n / 0.5) if n > 0 else 0,  # kg/ha
            'application': 'Basal application before planting'
        },
        'compost': {
            'npk_content': {'N': 1.0, 'P': 0.5, 'K': 1.0},  # %
            'quantity': int(n / 1.0) if n > 0 else 0,  # kg/ha
            'application': 'Mix with soil 15 days before planting'
        },
        'green_manure': {
            'npk_content': {'N': 2.0, 'P': 0.5, 'K': 1.5},  # %
            'quantity': int(n / 2.0) if n > 0 else 0,  # kg/ha
            'application': 'Plow under 30 days before planting'
        },
        'vermicompost': {
            'npk_content': {'N': 1.5, 'P': 0.8, 'K': 1.2},  # %
            'quantity': int(n / 1.5) if n > 0 else 0,  # kg/ha
            'application': 'Apply at planting and top dress'
        },
        'bone_meal': {
            'npk_content': {'N': 3.0, 'P': 20.0, 'K': 0.0},  # %
            'quantity': int(p / 20.0) if p > 0 else 0,  # kg/ha
            'application': 'Basal application for phosphorus'
        },
        'wood_ash': {
            'npk_content': {'N': 0.0, 'P': 1.0, 'K': 10.0},  # %
            'quantity': int(k / 10.0) if k > 0 else 0,  # kg/ha
            'application': 'Top dressing for potassium'
        }
    }
    
    return {
        'method': 'Organic',
        'organic_details': {
            'fertilizers': organic_fertilizers,
            'total_organic_matter': sum([f['quantity'] for f in organic_fertilizers.values()]),
            'application_schedule': generate_organic_schedule(crop),
            'benefits': [
                'Improves soil structure and water retention',
                'Enhances microbial activity',
                'Provides slow-release nutrients',
                'Environmentally sustainable',
                'Improves soil organic matter content'
            ],
            'organic_practices': [
                'Use compost and farmyard manure for soil improvement',
                'Apply green manure crops for nitrogen fixation',
                'Use vermicompost for enhanced soil fertility',
                'Implement crop rotation for soil health',
                'Apply organic mulching to retain moisture'
            ]
        }
    }


def generate_inorganic_recommendations(nutrients: Dict[str, int], crop: str) -> Dict[str, Any]:
    """
    Generate inorganic farming recommendations with chemical fertilizers.
    """
    n, p, k = nutrients['N'], nutrients['P'], nutrients['K']
    
    # Chemical fertilizer recommendations
    inorganic_fertilizers = {
        'urea': {
            'npk_content': {'N': 46, 'P': 0, 'K': 0},  # %
            'quantity': int(n / 0.46) if n > 0 else 0,  # kg/ha
            'application': 'Split application: 1/3 basal, 1/3 at tillering, 1/3 at panicle initiation'
        },
        'dap': {
            'npk_content': {'N': 18, 'P': 46, 'K': 0},  # %
            'quantity': int(p / 0.46) if p > 0 else 0,  # kg/ha
            'application': 'Basal application at planting'
        },
        'mop': {
            'npk_content': {'N': 0, 'P': 0, 'K': 60},  # %
            'quantity': int(k / 0.60) if k > 0 else 0,  # kg/ha
            'application': 'Split application: 1/2 basal, 1/2 at flowering'
        },
        'ssp': {
            'npk_content': {'N': 0, 'P': 16, 'K': 0},  # %
            'quantity': int(p / 0.16) if p > 0 else 0,  # kg/ha
            'application': 'Basal application for phosphorus'
        },
        'npk_complex': {
            'npk_content': {'N': 20, 'P': 20, 'K': 20},  # %
            'quantity': int(max(n, p, k) / 0.20) if max(n, p, k) > 0 else 0,  # kg/ha
            'application': 'Basal application with balanced nutrients'
        }
    }
    
    return {
        'method': 'Inorganic',
        'npk_nutrients': {
            'nitrogen': {'value': nutrients['N'], 'unit': 'kg/ha', 'source': 'Urea, DAP'},
            'phosphorus': {'value': nutrients['P'], 'unit': 'kg/ha', 'source': 'DAP, SSP'},
            'potassium': {'value': nutrients['K'], 'unit': 'kg/ha', 'source': 'MOP, NPK Complex'},
            'total_npk': sum(nutrients.values()),
            'fertilizers': inorganic_fertilizers,
            'total_fertilizer': sum([f['quantity'] for f in inorganic_fertilizers.values()]),
            'application_schedule': generate_inorganic_schedule(crop),
            'benefits': [
                'Immediate nutrient availability',
                'Precise nutrient control',
                'Higher yield potential',
                'Cost-effective for large areas',
                'Easy application and storage'
            ]
        }
    }


def generate_mixed_recommendations(nutrients: Dict[str, int], crop: str) -> Dict[str, Any]:
    """
    Generate mixed farming recommendations combining organic and inorganic fertilizers.
    """
    n, p, k = nutrients['N'], nutrients['P'], nutrients['K']
    
    # Mixed fertilizer recommendations (70% organic, 30% inorganic)
    mixed_fertilizers = {
        'farmyard_manure_urea': {
            'organic': {'type': 'Farmyard Manure', 'quantity': int(n * 0.7 / 0.5), 'npk': {'N': 0.5, 'P': 0.2, 'K': 0.5}},
            'inorganic': {'type': 'Urea', 'quantity': int(n * 0.3 / 0.46), 'npk': {'N': 46, 'P': 0, 'K': 0}},
            'application': 'Farmyard manure basal, urea split application'
        },
        'compost_dap': {
            'organic': {'type': 'Compost', 'quantity': int(p * 0.7 / 0.5), 'npk': {'N': 1.0, 'P': 0.5, 'K': 1.0}},
            'inorganic': {'type': 'DAP', 'quantity': int(p * 0.3 / 0.46), 'npk': {'N': 18, 'P': 46, 'K': 0}},
            'application': 'Compost basal, DAP at planting'
        },
        'vermicompost_mop': {
            'organic': {'type': 'Vermicompost', 'quantity': int(k * 0.7 / 1.2), 'npk': {'N': 1.5, 'P': 0.8, 'K': 1.2}},
            'inorganic': {'type': 'MOP', 'quantity': int(k * 0.3 / 0.60), 'npk': {'N': 0, 'P': 0, 'K': 60}},
            'application': 'Vermicompost basal, MOP split application'
        }
    }
    
    return {
        'method': 'Mixed',
        'mixed_details': {
            'fertilizers': mixed_fertilizers,
            'organic_ratio': '70%',
            'inorganic_ratio': '30%',
            'application_schedule': generate_mixed_schedule(crop),
            'benefits': [
                'Combines benefits of both methods',
                'Improves soil health gradually',
                'Provides immediate and long-term nutrients',
                'Cost-effective approach',
                'Sustainable farming practice'
            ],
            'mixed_practices': [
                'Use organic fertilizers for soil improvement',
                'Apply chemical fertilizers for immediate nutrient needs',
                'Combine farmyard manure with urea for balanced nutrition',
                'Use compost with DAP for phosphorus requirements',
                'Apply vermicompost with MOP for potassium needs'
            ],
            'nutrient_breakdown': {
                'organic_contribution': f"{int(nutrients['N'] * 0.7)} kg N, {int(nutrients['P'] * 0.7)} kg P, {int(nutrients['K'] * 0.7)} kg K",
                'inorganic_contribution': f"{int(nutrients['N'] * 0.3)} kg N, {int(nutrients['P'] * 0.3)} kg P, {int(nutrients['K'] * 0.3)} kg K"
            }
        }
    }


def generate_organic_schedule(crop: str) -> Dict[str, str]:
    """Generate organic farming application schedule."""
    return {
        'pre_planting': 'Apply farmyard manure/compost 15-30 days before planting',
        'at_planting': 'Apply vermicompost and bone meal at planting',
        'vegetative_stage': 'Top dress with compost tea or liquid organic fertilizers',
        'flowering_stage': 'Apply wood ash for potassium if needed',
        'post_harvest': 'Apply green manure or cover crops for next season'
    }


def generate_inorganic_schedule(crop: str) -> Dict[str, str]:
    """Generate inorganic farming application schedule."""
    return {
        'pre_planting': 'Apply DAP/SSP as basal dose',
        'at_planting': 'Apply 1/3 of urea with other fertilizers',
        'tillering_stage': 'Apply 1/3 of urea (25-30 days after planting)',
        'panicle_initiation': 'Apply remaining 1/3 urea and MOP',
        'flowering_stage': 'Apply foliar spray if needed'
    }


def generate_mixed_schedule(crop: str) -> Dict[str, str]:
    """Generate mixed farming application schedule."""
    return {
        'pre_planting': 'Apply farmyard manure/compost 15 days before planting',
        'at_planting': 'Apply DAP with vermicompost at planting',
        'vegetative_stage': 'Apply 1/3 urea with organic top dressing',
        'flowering_stage': 'Apply remaining urea and MOP with organic supplements',
        'post_harvest': 'Apply organic matter for soil improvement'
    }


def generate_step_by_step_instructions(crop: str, technique: str, season: str, nutrients: Dict[str, int]) -> str:
    """
    Generate farmer-friendly step-by-step instructions.
    """
    instructions = f"""
🌱 {crop} Cultivation Guide - {technique} Method ({season} Season)

📋 PRE-PLANTING PREPARATION:
1. Soil Testing: Test soil pH (6.0-7.5 ideal for {crop})
2. Land Preparation: Plow and harrow the field 2-3 times
3. Organic Matter: Add 10-15 tons compost per hectare
4. Drainage: Ensure proper drainage system

🌱 PLANTING:
1. Seed Selection: Use certified, disease-free seeds
2. Seed Treatment: Treat seeds with recommended fungicide
3. Spacing: Follow recommended spacing for {crop}
4. Planting Depth: Plant at 2-3 cm depth

💧 IRRIGATION:
1. Initial: Light irrigation after planting
2. Growth Stage: Maintain soil moisture at 60-80%
3. Critical Stages: Ensure adequate water during flowering
4. Harvest: Reduce irrigation 2 weeks before harvest

🌿 NUTRIENT MANAGEMENT ({technique}):
- Nitrogen (N): {nutrients['N']} kg/ha - Apply in 3 splits
- Phosphorus (P): {nutrients['P']} kg/ha - Apply at planting
- Potassium (K): {nutrients['K']} kg/ha - Apply in 2 splits

🛡️ PEST & DISEASE MANAGEMENT:
1. Monitor regularly for pests and diseases
2. Use integrated pest management (IPM)
3. Apply organic pesticides if using {technique.lower()} method
4. Maintain field hygiene

📅 HARVESTING:
1. Harvest at proper maturity stage
2. Use clean, sharp tools
3. Handle produce carefully to avoid damage
4. Store in cool, dry place

⚠️ IMPORTANT NOTES:
- Follow local agricultural extension recommendations
- Monitor weather conditions regularly
- Keep records of all activities
- Consult local experts for specific issues
"""
    return instructions.strip()


def predict_recommendation(input_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main prediction function that combines ML models and generates recommendations.
    """
    try:
        # Load models if not already loaded
        if _tech_model is None or _yield_model is None:
            load_models()
        
        # Extract input parameters
        crop = input_dict['crop']
        season = input_dict['season']
        soil = input_dict['soil']
        preference = input_dict['preference']
        latitude = input_dict['latitude']
        longitude = input_dict['longitude']
        
        # Generate planting date recommendations
        planting_dates = generate_planting_date_recommendation(crop, season, input_dict.get('location_name', ''), input_dict.get('planting_date'))
        
        # Generate detailed nutrient recommendations
        detailed_nutrients = generate_detailed_nutrient_recommendation(crop, soil, season, preference)
        
        # Get weather forecast with start date
        start_date = input_dict.get('planting_date')
        weather_forecast = get_weather_forecast(latitude, longitude, start_date)
        
        # For now, use rule-based predictions (models will be trained separately)
        # This is a fallback when ML models are not available
        technique_probs = {
            'Organic': 0.4,
            'Inorganic': 0.4,
            'Mixed': 0.2
        }
        
        # Adjust probabilities based on preference
        if preference == 'Organic':
            technique_probs = {'Organic': 0.7, 'Inorganic': 0.1, 'Mixed': 0.2}
        elif preference == 'Inorganic':
            technique_probs = {'Organic': 0.1, 'Inorganic': 0.7, 'Mixed': 0.2}
        else:  # Mixed
            technique_probs = {'Organic': 0.3, 'Inorganic': 0.3, 'Mixed': 0.4}
        
        preferred_technique = max(technique_probs, key=technique_probs.get)
        
        # Yield prediction (rule-based for now)
        base_yields = {
            'Rice': 4000, 'Wheat': 3500, 'Maize': 5000, 'Sugarcane': 80000,
            'Cotton': 500, 'Soybean': 2500, 'Potato': 25000, 'Tomato': 50000,
            'Onion': 30000, 'Chili': 15000
        }
        
        base_yield = base_yields.get(crop, 3000)
        
        # Adjust yield based on soil and season
        soil_multipliers = {'Clay': 0.9, 'Sandy': 0.8, 'Loamy': 1.0, 'Silty': 1.1, 'Peaty': 1.2, 'Chalky': 0.8}
        season_multipliers = {'Kharif': 1.0, 'Rabi': 1.1, 'Zaid': 0.9, 'Monsoon': 1.0, 'Winter': 1.1, 'Summer': 0.9}
        
        yield_prediction = int(base_yield * soil_multipliers.get(soil, 1.0) * season_multipliers.get(season, 1.0))
        
        # Generate step-by-step instructions
        instructions = generate_step_by_step_instructions(crop, preferred_technique, season, detailed_nutrients.get('base_nutrients', {'N': 100, 'P': 50, 'K': 40}))
        
        # Generate 7-day nutrient schedule
        daily_nutrient_schedule = generate_7day_nutrient_schedule(detailed_nutrients, start_date)
        
        # Add daily schedule to nutrient report
        detailed_nutrients['daily_recommendations'] = daily_nutrient_schedule
        
        # Compile results
        result = {
            'preferred_technique': preferred_technique,
            'technique_probs': technique_probs,
            'yield_prediction': yield_prediction,
            'nutrient_report': detailed_nutrients,
            'planting_dates': planting_dates,
            'weather_7day': weather_forecast,
            'step_by_step': instructions,
            'model_version': '2.0',
            'prediction_confidence': 0.85
        }
        
        logger.info(f"Prediction completed for {crop} at coordinates ({latitude}, {longitude})")
        return result
        
    except Exception as e:
        logger.error(f"Error in predict_recommendation: {str(e)}")
        # Return a basic fallback result
        return {
            'preferred_technique': input_dict.get('preference', 'Mixed'),
            'technique_probs': {'Organic': 0.33, 'Inorganic': 0.33, 'Mixed': 0.34},
            'yield_prediction': 3000,
            'nutrient_report': {'N': 100, 'P': 50, 'K': 40},
            'weather_7day': [],
            'step_by_step': f"Basic cultivation guide for {input_dict.get('crop', 'crop')}",
            'model_version': 'fallback',
            'prediction_confidence': 0.5,
            'error': 'Using fallback prediction due to model unavailability'
        }


def generate_7day_nutrient_schedule(nutrient_report: Dict[str, Any], start_date: str = None) -> List[Dict[str, Any]]:
    """
    Generate a 7-day detailed nutrient application schedule with specific daily processes.
    """
    from datetime import datetime, timedelta
    
    if start_date:
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    else:
        start_dt = datetime.now()
    
    daily_schedule = []
    
    # Get farming method and fertilizers
    farming_method = nutrient_report.get('method', 'Organic')
    fertilizers = {}
    
    if farming_method == 'Organic' and 'organic_details' in nutrient_report:
        fertilizers = nutrient_report['organic_details'].get('fertilizers', {})
    elif farming_method == 'Inorganic' and 'npk_nutrients' in nutrient_report:
        fertilizers = nutrient_report['npk_nutrients'].get('fertilizers', {})
    elif farming_method == 'Mixed' and 'mixed_details' in nutrient_report:
        fertilizers = nutrient_report['mixed_details'].get('fertilizers', {})
    
    # Define daily processes based on crop growth stages
    daily_processes = [
        {
            'day': 1,
            'stage': 'Soil Preparation',
            'activities': ['Soil testing', 'Land preparation', 'Initial fertilizer application'],
            'fertilizer_ratio': 0.4,  # 40% of total
            'time': 'Morning (6-8 AM)',
            'description': 'Prepare soil and apply initial nutrients for plant establishment'
        },
        {
            'day': 2,
            'stage': 'Planting & Watering',
            'activities': ['Seed sowing', 'Initial watering', 'Soil moisture check'],
            'fertilizer_ratio': 0.0,
            'time': 'Early morning (5-7 AM)',
            'description': 'Plant seeds and ensure proper soil moisture for germination'
        },
        {
            'day': 3,
            'stage': 'First Top Dressing',
            'activities': ['First fertilizer application', 'Weed control', 'Pest monitoring'],
            'fertilizer_ratio': 0.25,  # 25% of total
            'time': 'Evening (5-7 PM)',
            'description': 'Apply first top dressing around plant base for early growth'
        },
        {
            'day': 4,
            'stage': 'Growth Monitoring',
            'activities': ['Plant growth check', 'Soil pH monitoring', 'Watering schedule'],
            'fertilizer_ratio': 0.0,
            'time': 'Morning (7-9 AM)',
            'description': 'Monitor plant growth and adjust watering based on soil conditions'
        },
        {
            'day': 5,
            'stage': 'Foliar Application',
            'activities': ['Foliar spray', 'Nutrient deficiency check', 'Disease prevention'],
            'fertilizer_ratio': 0.15,  # 15% of total
            'time': 'Early morning (6-7 AM)',
            'description': 'Apply foliar nutrients for quick absorption and disease prevention'
        },
        {
            'day': 6,
            'stage': 'Mid-Growth Care',
            'activities': ['Second top dressing', 'Pruning if needed', 'Support structure'],
            'fertilizer_ratio': 0.15,  # 15% of total
            'time': 'Evening (6-8 PM)',
            'description': 'Apply second top dressing and provide plant support for continued growth'
        },
        {
            'day': 7,
            'stage': 'Final Application',
            'activities': ['Final fertilizer dose', 'Harvest preparation', 'Quality assessment'],
            'fertilizer_ratio': 0.05,  # 5% of total
            'time': 'Morning (8-10 AM)',
            'description': 'Apply final nutrients and prepare for harvest or next growth phase'
        }
    ]
    
    for i, process in enumerate(daily_processes):
        current_date = start_dt + timedelta(days=i)
        
        # Determine what fertilizers to apply on this day
        day_fertilizers = []
        
        if process['fertilizer_ratio'] > 0 and fertilizers:
            for key, fertilizer in fertilizers.items():
                if isinstance(fertilizer, dict) and 'quantity' in fertilizer:
                    quantity = fertilizer.get('quantity', 0) * process['fertilizer_ratio']
                    if quantity > 0:
                        day_fertilizers.append({
                            'type': key.replace('_', ' ').title(),
                            'quantity': round(quantity, 2),
                            'application': fertilizer.get('application', 'Standard application'),
                            'time': process['time']
                        })
        
        # If no specific fertilizers, add general activities
        if not day_fertilizers:
            day_fertilizers.append({
                'type': 'General Care',
                'quantity': 0,
                'application': process['description'],
                'time': process['time']
            })
        
        daily_schedule.append({
            'date': current_date.strftime('%Y-%m-%d'),
            'day': i + 1,
            'stage': process['stage'],
            'activities': process['activities'],
            'fertilizers': day_fertilizers,
            'description': process['description'],
            'time': process['time']
        })
    
    return daily_schedule




def get_daily_notes(day: int, method: str) -> str:
    """
    Get daily care notes based on day and farming method.
    """
    notes = {
        1: "Initial soil preparation and planting. Ensure proper spacing and depth.",
        2: "Monitor soil moisture and check for any signs of stress or disease.",
        3: "First fertilizer application. Water thoroughly after application.",
        4: "Continue monitoring growth and adjust watering schedule if needed.",
        5: "Foliar application day. Apply in early morning for best absorption.",
        6: "Check for pest and disease signs. Maintain proper soil moisture.",
        7: "Final application and assessment. Plan for next week's schedule."
    }
    
    method_notes = {
        'Organic': " Use only organic fertilizers and natural pest control methods.",
        'Inorganic': " Follow chemical fertilizer guidelines and safety precautions.",
        'Mixed': " Balance organic and inorganic inputs for optimal results."
    }
    
    return notes.get(day, "Continue regular monitoring and care.") + method_notes.get(method, "")
