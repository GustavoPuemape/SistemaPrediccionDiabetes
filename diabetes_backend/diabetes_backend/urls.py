# diabetes_backend/urls.py

from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def api_root(request):
    """Vista raíz de la API"""
    return JsonResponse({
        'message': 'API de Predicción de Diabetes',
        'version': '1.0',
        'endpoints': {
            'predict': '/api/predict/',
            'explanation': '/api/predict/explanation/',
            'predictions': '/api/predictions/',
            'stats': '/api/predictions/stats/',
            'admin': '/admin/',
        }
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('predictor.urls')),
    path('', api_root, name='api-root'),
]
