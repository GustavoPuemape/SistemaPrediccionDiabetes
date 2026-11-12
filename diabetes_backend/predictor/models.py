# predictor/models.py

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Prediction(models.Model):
    """
    Modelo para almacenar el historial de predicciones
    """
    # Campos de entrada del usuario
    age = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(120)],
        help_text="Edad del paciente en años"
    )
    pulse_rate = models.FloatField(
        validators=[MinValueValidator(30), MaxValueValidator(200)],
        help_text="Frecuencia cardíaca en latidos por minuto"
    )
    systolic_bp = models.FloatField(
        validators=[MinValueValidator(70), MaxValueValidator(250)],
        help_text="Presión arterial sistólica en mmHg"
    )
    diastolic_bp = models.FloatField(
        validators=[MinValueValidator(40), MaxValueValidator(150)],
        help_text="Presión arterial diastólica en mmHg"
    )
    glucose = models.FloatField(
        validators=[MinValueValidator(50), MaxValueValidator(500)],
        help_text="Nivel de glucosa en mg/dL"
    )
    height = models.FloatField(
        validators=[MinValueValidator(50), MaxValueValidator(250)],
        help_text="Altura en centímetros"
    )
    weight = models.FloatField(
        validators=[MinValueValidator(20), MaxValueValidator(300)],
        help_text="Peso en kilogramos"
    )
    bmi = models.FloatField(
        validators=[MinValueValidator(10), MaxValueValidator(70)],
        help_text="Índice de masa corporal"
    )
    
    # Campos binarios
    family_diabetes = models.BooleanField(
        default=False,
        help_text="Historial familiar de diabetes"
    )
    hypertensive = models.BooleanField(
        default=False,
        help_text="Paciente hipertenso"
    )
    family_hypertension = models.BooleanField(
        default=False,
        help_text="Historial familiar de hipertensión"
    )
    cardiovascular_disease = models.BooleanField(
        default=False,
        help_text="Enfermedad cardiovascular"
    )
    stroke = models.BooleanField(
        default=False,
        help_text="Historial de derrame cerebral"
    )
    
    # Resultados de la predicción
    prediction = models.BooleanField(
        help_text="Predicción: True = Diabético, False = No diabético"
    )
    probability = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        help_text="Probabilidad de diabetes (0-1)"
    )
    risk_level = models.CharField(
        max_length=20,
        choices=[
            ('BAJO', 'Riesgo Bajo'),
            ('MODERADO', 'Riesgo Moderado'),
            ('ALTO', 'Riesgo Alto'),
            ('MUY_ALTO', 'Riesgo Muy Alto'),
        ],
        help_text="Nivel de riesgo calculado"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Predicción"
        verbose_name_plural = "Predicciones"
    
    def __str__(self):
        return f"Predicción {self.id} - {'Diabético' if self.prediction else 'No Diabético'} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"
    
    def get_risk_level(self):
        """Retorna el nivel de riesgo legible"""
        risk_levels = {
            'BAJO': 'Riesgo Bajo',
            'MODERADO': 'Riesgo Moderado',
            'ALTO': 'Riesgo Alto',
            'MUY_ALTO': 'Riesgo Muy Alto',
        }
        return risk_levels.get(self.risk_level, 'Desconocido')