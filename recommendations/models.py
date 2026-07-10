from django.db import models
from django.utils import timezone


class Recommendation(models.Model):
    """
    Model to store crop recommendations with ML predictions and weather data.
    """
    CROP_CHOICES = [
        ('Rice', 'Rice'),
        ('Wheat', 'Wheat'),
        ('Maize', 'Maize'),
        ('Sugarcane', 'Sugarcane'),
        ('Cotton', 'Cotton'),
        ('Soybean', 'Soybean'),
        ('Potato', 'Potato'),
        ('Tomato', 'Tomato'),
        ('Onion', 'Onion'),
        ('Chili', 'Chili'),
    ]
    
    SEASON_CHOICES = [
        ('Kharif', 'Kharif'),
        ('Rabi', 'Rabi'),
        ('Zaid', 'Zaid'),
        ('Monsoon', 'Monsoon'),
        ('Winter', 'Winter'),
        ('Summer', 'Summer'),
    ]
    
    SOIL_CHOICES = [
        ('Clay', 'Clay'),
        ('Sandy', 'Sandy'),
        ('Loamy', 'Loamy'),
        ('Silty', 'Silty'),
        ('Peaty', 'Peaty'),
        ('Chalky', 'Chalky'),
    ]
    
    PREFERENCE_CHOICES = [
        ('Organic', 'Organic'),
        ('Inorganic', 'Inorganic'),
        ('Mixed', 'Mixed'),
    ]

    # Input fields
    crop = models.CharField(max_length=50, choices=CROP_CHOICES)
    season = models.CharField(max_length=50, choices=SEASON_CHOICES)
    soil = models.CharField(max_length=50, choices=SOIL_CHOICES)
    preference = models.CharField(max_length=50, choices=PREFERENCE_CHOICES)
    location_name = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    
    # ML prediction results stored as JSON
    result_json = models.JSONField(default=dict)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['crop']),
            models.Index(fields=['season']),
            models.Index(fields=['created_at']),
            models.Index(fields=['location_name']),
        ]
    
    def __str__(self):
        return f"{self.crop} recommendation for {self.location_name} ({self.created_at.strftime('%Y-%m-%d')})"
    
    @property
    def preferred_technique(self):
        """Extract preferred technique from result_json."""
        return self.result_json.get('preferred_technique', 'Unknown')
    
    @property
    def yield_prediction(self):
        """Extract yield prediction from result_json."""
        return self.result_json.get('yield_prediction', 0)
    
    @property
    def weather_forecast(self):
        """Extract weather forecast from result_json."""
        return self.result_json.get('weather_7day', [])
