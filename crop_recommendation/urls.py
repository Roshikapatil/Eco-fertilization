"""
URL configuration for crop_recommendation project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

def home_view(request):
    """Home page for the crop recommendation API."""
    if request.headers.get('Accept', '').startswith('application/json'):
        # Return JSON for API requests
        return JsonResponse({
            'message': 'Crop Recommendation API',
            'version': '2.0',
            'endpoints': {
                'recommend': '/api/recommend/',
                'history': '/api/recommend/history/',
                'status': '/api/status/',
                'admin': '/admin/'
            },
            'features': [
                'Dynamic crop-specific scheduling',
                '4-6 months full cycle planning',
                'Precise fertilizer calculations',
                'Growth stage mapping',
                'Harvest timing indicators'
            ]
        })
    else:
        # Return HTML for browser requests
        return render(request, 'home.html')

urlpatterns = [
    path('', home_view, name='home'),
    path('admin/', admin.site.urls),
    path('api/', include('recommendations.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
