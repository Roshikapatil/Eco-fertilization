from django.contrib import admin
from .models import Recommendation


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'crop', 'season', 'soil', 'preference', 
        'location_name', 'preferred_technique', 'yield_prediction', 'created_at'
    ]
    list_filter = ['crop', 'season', 'soil', 'preference', 'created_at']
    search_fields = ['location_name', 'crop']
    readonly_fields = ['created_at', 'updated_at', 'result_json']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Input Parameters', {
            'fields': ('crop', 'season', 'soil', 'preference', 'location_name', 'latitude', 'longitude')
        }),
        ('ML Results', {
            'fields': ('result_json',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def preferred_technique(self, obj):
        return obj.preferred_technique
    preferred_technique.short_description = 'Technique'
    
    def yield_prediction(self, obj):
        return f"{obj.yield_prediction} kg/ha" if obj.yield_prediction else "N/A"
    yield_prediction.short_description = 'Predicted Yield'
