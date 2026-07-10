from rest_framework import serializers
from .models import Recommendation


class RecommendationInputSerializer(serializers.Serializer):
    """
    Serializer for validating input data for crop recommendations.
    """
    crop = serializers.ChoiceField(choices=Recommendation.CROP_CHOICES)
    season = serializers.ChoiceField(choices=Recommendation.SEASON_CHOICES)
    soil = serializers.ChoiceField(choices=Recommendation.SOIL_CHOICES)
    preference = serializers.ChoiceField(choices=Recommendation.PREFERENCE_CHOICES)
    location_name = serializers.CharField(max_length=100)
    latitude = serializers.FloatField(min_value=-90, max_value=90)
    longitude = serializers.FloatField(min_value=-180, max_value=180)
    
    def validate_location_name(self, value):
        """Validate location name is not empty."""
        if not value.strip():
            raise serializers.ValidationError("Location name cannot be empty.")
        return value.strip()
    
    def validate(self, data):
        """Cross-field validation."""
        # Validate that coordinates are reasonable for the given location
        lat, lon = data['latitude'], data['longitude']
        
        # Basic coordinate validation (can be enhanced with location-specific checks)
        if lat == 0 and lon == 0:
            raise serializers.ValidationError("Invalid coordinates: (0, 0) is not a valid location.")
        
        return data


class RecommendationSerializer(serializers.ModelSerializer):
    """
    Serializer for Recommendation model instances.
    """
    preferred_technique = serializers.ReadOnlyField()
    yield_prediction = serializers.ReadOnlyField()
    weather_forecast = serializers.ReadOnlyField()
    nutrient_report = serializers.SerializerMethodField()
    step_by_step_guide = serializers.SerializerMethodField()
    weather_7day = serializers.SerializerMethodField()
    planting_dates = serializers.SerializerMethodField()
    
    class Meta:
        model = Recommendation
        fields = [
            'id', 'crop', 'season', 'soil', 'preference', 
            'location_name', 'latitude', 'longitude',
            'result_json', 'preferred_technique', 'yield_prediction',
            'weather_forecast', 'nutrient_report', 'step_by_step_guide',
            'weather_7day', 'planting_dates', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_nutrient_report(self, obj):
        """Extract nutrient report from result_json."""
        return obj.result_json.get('nutrient_report', {})
    
    def get_step_by_step_guide(self, obj):
        """Extract step-by-step guide from result_json."""
        return obj.result_json.get('step_by_step', '')
    
    def get_weather_7day(self, obj):
        """Extract 7-day weather forecast from result_json."""
        return obj.result_json.get('weather_7day', [])
    
    def get_planting_dates(self, obj):
        """Extract planting dates from result_json."""
        return obj.result_json.get('planting_dates', {})


class RecommendationHistorySerializer(serializers.ModelSerializer):
    """
    Simplified serializer for recommendation history listing.
    """
    preferred_technique = serializers.ReadOnlyField()
    yield_prediction = serializers.ReadOnlyField()
    
    class Meta:
        model = Recommendation
        fields = [
            'id', 'crop', 'season', 'soil', 'preference',
            'location_name', 'preferred_technique', 'yield_prediction',
            'created_at'
        ]
