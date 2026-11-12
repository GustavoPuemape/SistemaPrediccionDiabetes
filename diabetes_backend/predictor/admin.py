# predictor/admin.py

from django.contrib import admin
from django.utils.html import format_html
from .models import Prediction

@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para Prediction
    """
    list_display = (
        'id', 
        'age', 
        'glucose', 
        'bmi', 
        'prediction_badge', 
        'probability_display',
        'risk_level_badge',
        'created_at'
    )
    
    list_filter = (
        'prediction',
        'risk_level',
        'hypertensive',
        'family_diabetes',
        'created_at'
    )
    
    search_fields = (
        'id',
        'age',
        'glucose'
    )
    
    readonly_fields = (
        'prediction',
        'probability',
        'risk_level',
        'created_at',
        'updated_at'
    )
    
    fieldsets = (
        ('Información del Paciente', {
            'fields': (
                'age',
                'pulse_rate',
                ('height', 'weight', 'bmi')
            )
        }),
        ('Mediciones Médicas', {
            'fields': (
                ('systolic_bp', 'diastolic_bp'),
                'glucose',
            )
        }),
        ('Historial Médico', {
            'fields': (
                'family_diabetes',
                'hypertensive',
                'family_hypertension',
                'cardiovascular_disease',
                'stroke'
            )
        }),
        ('Resultados de la Predicción', {
            'fields': (
                'prediction',
                'probability',
                'risk_level',
            )
        }),
        ('Metadata', {
            'fields': (
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        })
    )
    
    ordering = ('-created_at',)
    
    date_hierarchy = 'created_at'
    
    def prediction_badge(self, obj):
        """Muestra un badge colorido para la predicción"""
        if obj.prediction:
            color = 'red'
            text = '⚠️ Diabético'
        else:
            color = 'green'
            text = '✅ No Diabético'
        
        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 3px 10px; border-radius: 5px;">{}</span>',
            color,
            text
        )
    prediction_badge.short_description = 'Predicción'
    
    def probability_display(self, obj):
        """Muestra la probabilidad como porcentaje con barra"""
        percentage = obj.probability * 100
        color = self._get_probability_color(percentage)
        
        return format_html(
            '<div style="width: 100px; background-color: #f0f0f0; '
            'border-radius: 3px; overflow: hidden;">'
            '<div style="width: {}%; background-color: {}; '
            'color: white; text-align: center; padding: 2px 0;">'
            '{:.1f}%</div></div>',
            percentage,
            color,
            percentage
        )
    probability_display.short_description = 'Probabilidad'
    
    def risk_level_badge(self, obj):
        """Muestra un badge para el nivel de riesgo"""
        colors = {
            'BAJO': '#28a745',
            'MODERADO': '#ffc107',
            'ALTO': '#fd7e14',
            'MUY_ALTO': '#dc3545'
        }
        
        labels = {
            'BAJO': 'Bajo',
            'MODERADO': 'Moderado',
            'ALTO': 'Alto',
            'MUY_ALTO': 'Muy Alto'
        }
        
        color = colors.get(obj.risk_level, '#6c757d')
        label = labels.get(obj.risk_level, 'Desconocido')
        
        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 3px 10px; border-radius: 5px; font-weight: bold;">{}</span>',
            color,
            label
        )
    risk_level_badge.short_description = 'Nivel de Riesgo'
    
    def _get_probability_color(self, percentage):
        """Retorna el color según el porcentaje de probabilidad"""
        if percentage < 25:
            return '#28a745'  # Verde
        elif percentage < 50:
            return '#ffc107'  # Amarillo
        elif percentage < 75:
            return '#fd7e14'  # Naranja
        else:
            return '#dc3545'  # Rojo
    
    def has_add_permission(self, request):
        """Deshabilitar creación manual desde admin"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Permitir eliminación solo a superusuarios"""
        return request.user.is_superuser