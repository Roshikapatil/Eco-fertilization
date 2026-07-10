from django.urls import path
from . import views

urlpatterns = [
    path('recommend/', views.recommend_crop, name='recommend_crop'),
    path('recommend/history/', views.RecommendationHistoryView.as_view(), name='recommendation_history'),
    path('recommend/<int:pk>/', views.recommendation_detail, name='recommendation_detail'),
    path('status/', views.api_status, name='api_status'),
]
