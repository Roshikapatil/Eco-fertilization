# Crop Recommendation System - Backend

A comprehensive Django REST API backend for crop recommendation system with machine learning integration, MySQL database, and real-time weather data.

## 🌟 Features

- **Django REST Framework** API with comprehensive endpoints
- **MySQL Database** integration with optimized models
- **Machine Learning Pipeline** with RandomForest and XGBoost models
- **Real-time Weather Integration** via OpenWeather API
- **Production-ready** configuration with logging and error handling
- **Comprehensive API Documentation** with filtering and pagination

## 🏗️ Architecture

```
crop_recommendation_backend/
├── crop_recommendation/          # Django project settings
│   ├── settings.py              # Main configuration
│   ├── urls.py                  # URL routing
│   └── wsgi.py                  # WSGI configuration
├── recommendations/             # Main app
│   ├── models.py               # Database models
│   ├── serializers.py          # API serializers
│   ├── views.py                # API views
│   ├── urls.py                 # App URL routing
│   ├── admin.py                # Django admin
│   └── ml_predict.py           # ML prediction module
├── ml/                         # Machine Learning
│   └── train.py                # Model training script
├── models/                     # Trained ML models
├── requirements.txt            # Python dependencies
└── manage.py                   # Django management script
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- MySQL 5.7+
- pip (Python package manager)

### Installation

1. **Clone and navigate to the project:**
   ```bash
   cd crop_recommendation_backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp env_example.txt .env
   # Edit .env with your configuration
   ```

5. **Set up MySQL database:**
   ```sql
   CREATE DATABASE crop_recommendation;
   CREATE USER 'crop_user'@'localhost' IDENTIFIED BY 'your_password';
   GRANT ALL PRIVILEGES ON crop_recommendation.* TO 'crop_user'@'localhost';
   FLUSH PRIVILEGES;
   ```

6. **Run migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

7. **Create superuser:**
   ```bash
   python manage.py createsuperuser
   ```

8. **Train ML models:**
   ```bash
   python ml/train.py
   ```

9. **Start development server:**
   ```bash
   python manage.py runserver
   ```

## 📊 API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/recommend/` | Get crop recommendation |
| `GET` | `/api/recommend/history/` | Get recommendation history |
| `GET` | `/api/recommend/{id}/` | Get specific recommendation |
| `GET` | `/api/status/` | API health check |

### Request/Response Examples

#### Get Crop Recommendation
```bash
POST /api/recommend/
Content-Type: application/json

{
  "crop": "Rice",
  "season": "Monsoon",
  "soil": "Loamy",
  "preference": "Organic",
  "location_name": "Delhi",
  "latitude": 28.7041,
  "longitude": 77.1025
}
```

**Response:**
```json
{
  "id": 1,
  "crop": "Rice",
  "season": "Monsoon",
  "soil": "Loamy",
  "preference": "Organic",
  "location_name": "Delhi",
  "latitude": 28.7041,
  "longitude": 77.1025,
  "result_json": {
    "preferred_technique": "Organic",
    "technique_probs": {
      "Organic": 0.7,
      "Inorganic": 0.1,
      "Mixed": 0.2
    },
    "yield_prediction": 4200,
    "nutrient_report": {
      "N": 120,
      "P": 60,
      "K": 40
    },
    "weather_7day": [
      {
        "day": "2024-01-01",
        "temperature": 25.0,
        "humidity": 60,
        "rainfall": 0,
        "description": "clear sky"
      }
    ],
    "step_by_step": "🌱 Rice Cultivation Guide - Organic Method..."
  },
  "created_at": "2024-01-01T10:00:00Z"
}
```

#### Get Recommendation History
```bash
GET /api/recommend/history/?crop=Rice&start_date=2024-01-01&page=1
```

## 🤖 Machine Learning

### Model Training

The system includes two ML models:

1. **RandomForest Classifier** - Predicts fertilizer technique (Organic/Inorganic/Mixed)
2. **XGBoost Regressor** - Predicts crop yield

**Train models:**
```bash
python ml/train.py
```

**Model Features:**
- Crop type, season, soil type, preference
- Location coordinates (latitude, longitude)
- Soil nutrients (N, P, K, pH)
- Weather data (rainfall, temperature, humidity)

### Prediction Pipeline

1. **Input Validation** - Validates and preprocesses input data
2. **Feature Engineering** - Converts categorical to numerical features
3. **Model Prediction** - Uses trained models for predictions
4. **Weather Integration** - Fetches real-time weather data
5. **Recommendation Generation** - Creates farmer-friendly instructions

## 🌤️ Weather Integration

The system integrates with OpenWeather API for real-time weather data:

- **7-day forecast** for the specified location
- **Temperature, humidity, rainfall** predictions
- **Fallback data** when API is unavailable

**Setup:**
1. Get API key from [OpenWeather](https://openweathermap.org/api)
2. Add to `.env`: `OPENWEATHER_API_KEY=your_key_here`

## 🗄️ Database Schema

### Recommendation Model

| Field | Type | Description |
|-------|------|-------------|
| `id` | AutoField | Primary key |
| `crop` | CharField | Crop type (Rice, Wheat, etc.) |
| `season` | CharField | Growing season |
| `soil` | CharField | Soil type |
| `preference` | CharField | Farming preference |
| `location_name` | CharField | Location name |
| `latitude` | FloatField | GPS latitude |
| `longitude` | FloatField | GPS longitude |
| `result_json` | JSONField | ML predictions and results |
| `created_at` | DateTimeField | Creation timestamp |
| `updated_at` | DateTimeField | Last update timestamp |

## 🔧 Configuration

### Environment Variables

```bash
# Django
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=crop_recommendation
DB_USER=root
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=3306

# APIs
OPENWEATHER_API_KEY=your-api-key
```

### Production Settings

For production deployment:

1. **Set DEBUG=False**
2. **Use strong SECRET_KEY**
3. **Configure proper ALLOWED_HOSTS**
4. **Use production database**
5. **Set up proper logging**
6. **Use HTTPS**

## 📈 Performance & Monitoring

### Logging

- **File logging** to `logs/django.log`
- **Console logging** for development
- **Structured logging** with timestamps

### Database Optimization

- **Indexes** on frequently queried fields
- **Pagination** for large result sets
- **Query optimization** with select_related

### API Performance

- **Response caching** for weather data
- **Async processing** for ML predictions
- **Error handling** with fallback responses

## 🧪 Testing

### Run Tests
```bash
python manage.py test
```

### API Testing
```bash
# Test recommendation endpoint
curl -X POST http://localhost:8000/api/recommend/ \
  -H "Content-Type: application/json" \
  -d '{"crop":"Rice","season":"Monsoon","soil":"Loamy","preference":"Organic","location_name":"Delhi","latitude":28.7041,"longitude":77.1025}'
```

## 🚀 Deployment

### Using Gunicorn

```bash
pip install gunicorn
gunicorn crop_recommendation.wsgi:application --bind 0.0.0.0:8000
```

### Using Docker (Optional)

```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "crop_recommendation.wsgi:application", "--bind", "0.0.0.0:8000"]
```

## 🔒 Security

- **Token Authentication** for API access
- **CORS configuration** for frontend integration
- **Input validation** and sanitization
- **SQL injection protection** via Django ORM
- **Environment variable** for sensitive data

## 📝 API Documentation

### Filtering & Pagination

**History endpoint supports:**
- `crop` - Filter by crop type
- `season` - Filter by season
- `start_date` / `end_date` - Date range filtering
- `location` - Location name search
- `page` - Pagination (20 items per page)

### Error Handling

All endpoints return consistent error responses:

```json
{
  "error": "Error message",
  "details": "Additional error details"
}
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Add tests
5. Submit pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the logs in `logs/django.log`
2. Verify database connection
3. Ensure all environment variables are set
4. Check ML models are trained and available

---

**Built with ❤️ for sustainable agriculture**
#   E c o - f e r t i l i z a t i o n  
 