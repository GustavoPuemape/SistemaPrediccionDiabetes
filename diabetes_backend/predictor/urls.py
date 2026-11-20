# predictor/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PredictionAPIView, PredictionViewSet

# Crear router para el ViewSet
router = DefaultRouter()
router.register(r'predictions', PredictionViewSet, basename='prediction')

urlpatterns = [
    # Endpoint principal de predicción
    path('predict/', PredictionAPIView.as_view(), name='predict'),
    
    # Incluir rutas del router (historial y estadísticas)
    path('', include(router.urls)),
]
