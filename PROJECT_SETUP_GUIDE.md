# 🌱 Crop Recommendation System - Complete Setup Guide

## 📋 **Project Overview**

This is a comprehensive crop recommendation system that provides:
- **Smart Crop Recommendations** based on location, soil, season, and farming preference
- **7-Day Weather Forecasting** with planting date accuracy
- **Detailed Nutrient Reports** tailored to farming methods (Organic/Inorganic/Mixed)
- **Interactive Maps** for location selection
- **Full-Screen Modern UI** with responsive design
- **Real-time Data** and comprehensive reporting

## 🚀 **Quick Start Guide**

### **Prerequisites**
- Python 3.12+ installed
- Modern web browser (Chrome, Firefox, Edge)
- Internet connection (for weather API)

### **Step 1: Install Dependencies**
```bash
# Navigate to project directory
cd crop_recommendation_backend

# Install Python dependencies
pip install -r requirements.txt
```

### **Step 2: Setup Database**
```bash
# Create database migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser
```

### **Step 3: Train ML Models**
```bash
# Train the machine learning models
python ml/train.py
```

### **Step 4: Start the Servers**

**Terminal 1 - Django Backend:**
```bash
python manage.py runserver
```
*Server will run on: http://127.0.0.1:8000*

**Terminal 2 - HTTP Server (for frontend):**
```bash
python -m http.server 8080
```
*Frontend will be available at: http://localhost:8080*

### **Step 5: Access the Application**
1. **Login Page:** http://localhost:8080/login.html
2. **Main Form:** http://localhost:8080/enhanced_crop_system_fixed.html
3. **API Status:** http://127.0.0.1:8000/api/status/

## 🎯 **Key Features Implemented**

### **1. Farming Preference-Based Display**
- **Organic Farming** → Shows organic details (compost, manure, practices)
- **Inorganic Farming** → Shows NPK nutrients (chemical fertilizers)
- **Mixed Farming** → Shows mixed details (combinations, ratios)

### **2. Comprehensive Reports**
- **Overview Tab:** Summary of recommendations
- **Weather Tab:** 7-day weather forecast
- **Nutrients Tab:** Detailed nutrient information based on farming method
- **Schedule Tab:** Application schedule for fertilizers
- **Guide Tab:** Step-by-step cultivation guide

### **3. Interactive Features**
- **Location Selection:** District dropdown + interactive map
- **Custom Planting Date:** User can specify when to start recommendations
- **Real-time Weather:** Accurate weather data for the specified date
- **Full-Screen UI:** Modern, responsive interface

### **4. Technical Features**
- **Machine Learning:** RandomForest + XGBoost models
- **Weather API:** OpenWeatherMap integration
- **Database:** SQLite (development) / MySQL (production)
- **CORS Support:** Cross-origin requests enabled
- **Error Handling:** Comprehensive error management

## 📁 **Project Structure**

```
crop_recommendation_backend/
├── crop_recommendation/          # Django project settings
│   ├── settings.py              # Main configuration
│   ├── urls.py                  # URL routing
│   └── wsgi.py                  # WSGI configuration
├── recommendations/              # Main app
│   ├── models.py                # Database models
│   ├── views.py                 # API endpoints
│   ├── serializers.py           # Data serialization
│   ├── urls.py                  # API routing
│   └── ml_predict.py            # ML prediction logic
├── ml/                          # Machine learning
│   ├── train.py                 # Model training script
│   └── models/                  # Trained model files
├── static/                      # Static files
├── templates/                   # HTML templates
├── enhanced_crop_system_fixed.html  # Main frontend
├── crop_results.html            # Results display page
├── login.html                   # Login page
├── requirements.txt             # Python dependencies
└── manage.py                    # Django management
```

## 🔧 **API Endpoints**

### **GET /api/status/**
- **Purpose:** Check API health
- **Response:** Server status and statistics

### **POST /api/recommend/**
- **Purpose:** Get crop recommendation
- **Body:**
  ```json
  {
    "crop": "Rice",
    "season": "Kharif", 
    "soil": "Loamy",
    "preference": "Organic",
    "location_name": "Delhi",
    "latitude": 28.6139,
    "longitude": 77.2090,
    "planting_date": "2025-09-25"
  }
  ```

### **GET /api/recommend/history/**
- **Purpose:** Get recommendation history
- **Response:** List of all recommendations

### **GET /api/recommend/{id}/**
- **Purpose:** Get specific recommendation
- **Response:** Detailed recommendation data

## 🌾 **Supported Crops**

- Rice, Wheat, Maize, Sugarcane
- Cotton, Soybean, Potato
- Tomato, Onion, Chili

## 🌍 **Supported Locations**

- **Indian Cities:** Delhi, Mumbai, Bangalore, Chennai, Kolkata, Hyderabad, Pune, Indore
- **Custom Locations:** Any coordinates worldwide
- **District Selection:** Quick selection from dropdown

## ⚙️ **Configuration**

### **Environment Variables (.env)**
```env
# Database (optional - defaults to SQLite)
USE_SQLITE=True
DB_NAME=crop_recommendation
DB_USER=root
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306

# Weather API (optional - uses mock data if not provided)
OPENWEATHER_API_KEY=your_api_key_here

# Google Maps (optional - uses fallback if not provided)
GOOGLE_MAPS_API_KEY=your_api_key_here
```

### **Django Settings**
- **Database:** SQLite (default) or MySQL
- **CORS:** Enabled for local development
- **Static Files:** Configured for production
- **Security:** Development settings included

## 🐛 **Troubleshooting**

### **Common Issues:**

1. **"ModuleNotFoundError: No module named 'MySQLdb'"**
   - **Solution:** The system automatically uses SQLite if MySQL is not available

2. **"Network Error" in frontend**
   - **Solution:** Ensure both servers are running (Django + HTTP server)

3. **"Schedule data not available"**
   - **Solution:** Fixed in latest version - schedule now shows correctly

4. **Weather API errors**
   - **Solution:** System uses mock data if API key is not provided

### **Testing the System:**
```bash
# Test API endpoints
python test_api_example.py

# Test farming preferences
python test_farming_preferences.py

# Test frontend display
python test_frontend_display.py
```

## 📊 **Performance Features**

- **Caching:** ML models loaded once and cached
- **Async Processing:** Non-blocking API responses
- **Error Recovery:** Graceful fallbacks for API failures
- **Responsive Design:** Works on desktop and mobile
- **Real-time Updates:** Live data refresh

## 🔒 **Security Features**

- **Input Validation:** All inputs sanitized
- **CORS Protection:** Configured for development
- **SQL Injection Prevention:** Django ORM protection
- **XSS Protection:** Output escaping enabled

## 📈 **Future Enhancements**

- **User Authentication:** User accounts and history
- **Advanced Analytics:** Crop yield predictions
- **Mobile App:** React Native version
- **Multi-language:** Support for regional languages
- **Export Features:** PDF/Excel report generation

## 🎉 **Success!**

Your crop recommendation system is now fully functional with:
- ✅ **Organic Farming Details** (compost, manure, practices)
- ✅ **Inorganic NPK Nutrients** (chemical fertilizers)
- ✅ **Mixed Farming Combinations** (organic + inorganic)
- ✅ **7-Day Weather Forecasts** with accurate dates
- ✅ **Application Schedules** for all farming methods
- ✅ **Interactive Maps** and location selection
- ✅ **Full-Screen Modern UI** with responsive design
- ✅ **Real-time Data** and comprehensive reporting

**Access your system at:** http://localhost:8080/enhanced_crop_system_fixed.html

---

*For support or questions, check the terminal logs or run the test scripts provided.*






