from rest_framework import status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from datetime import datetime, timedelta
import logging

from .models import Recommendation
from .serializers import (
    RecommendationInputSerializer, 
    RecommendationSerializer,
    RecommendationHistorySerializer
)
from .ml_predict import predict_recommendation

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([AllowAny])
def recommend_crop(request):
    """
    POST /api/recommend/
    Accepts JSON input and returns crop recommendation with ML predictions.
    """
    try:
        # Validate input data
        serializer = RecommendationInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        validated_data = serializer.validated_data
        
        # Convert to dict for ML prediction
        input_dict = {
            'crop': validated_data['crop'],
            'season': validated_data['season'],
            'soil': validated_data['soil'],
            'preference': validated_data['preference'],
            'latitude': validated_data['latitude'],
            'longitude': validated_data['longitude'],
        }
        
        # Get ML prediction
        try:
            prediction_result = predict_recommendation(input_dict)
            logger.info(f"ML prediction successful for {validated_data['crop']} at {validated_data['location_name']}")
        except Exception as e:
            logger.error(f"ML prediction failed: {str(e)}")
            return Response(
                {'error': 'Failed to generate recommendation. Please try again.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Create recommendation record
        recommendation_data = {
            **validated_data,
            'result_json': prediction_result
        }
        
        recommendation = Recommendation.objects.create(**recommendation_data)
        
        # Return the recommendation
        response_serializer = RecommendationSerializer(recommendation)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Unexpected error in recommend_crop: {str(e)}")
        return Response(
            {'error': 'An unexpected error occurred. Please try again.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class RecommendationHistoryView(ListAPIView):
    """
    GET /api/recommend/history/
    Returns paginated list of saved recommendations with filtering options.
    """
    serializer_class = RecommendationHistorySerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['crop', 'season', 'soil', 'preference']
    search_fields = ['location_name', 'crop']
    ordering_fields = ['created_at', 'crop', 'location_name']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = Recommendation.objects.all()
        
        # Date range filtering
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__date__gte=start_date)
            except ValueError:
                pass
        
        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__date__lte=end_date)
            except ValueError:
                pass
        
        # Location filtering
        location = self.request.query_params.get('location')
        if location:
            queryset = queryset.filter(
                Q(location_name__icontains=location) |
                Q(location_name__icontains=location.title())
            )
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        try:
            return super().list(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in RecommendationHistoryView: {str(e)}")
            return Response(
                {'error': 'Failed to retrieve recommendation history.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(['GET'])
@permission_classes([AllowAny])
def recommendation_detail(request, pk):
    """
    GET /api/recommend/{id}/
    Returns detailed information about a specific recommendation.
    """
    try:
        recommendation = Recommendation.objects.get(pk=pk)
        serializer = RecommendationSerializer(recommendation)
        return Response(serializer.data)
    except Recommendation.DoesNotExist:
        return Response(
            {'error': 'Recommendation not found.'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error in recommendation_detail: {str(e)}")
        return Response(
            {'error': 'Failed to retrieve recommendation details.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def api_status(request):
    """
    GET /api/status/
    Returns API status and basic information.
    """
    try:
        total_recommendations = Recommendation.objects.count()
        recent_recommendations = Recommendation.objects.filter(
            created_at__gte=datetime.now() - timedelta(days=7)
        ).count()
        
        return Response({
            'status': 'healthy',
            'total_recommendations': total_recommendations,
            'recent_recommendations': recent_recommendations,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error in api_status: {str(e)}")
        return Response(
            {'status': 'error', 'message': 'Failed to retrieve API status'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
