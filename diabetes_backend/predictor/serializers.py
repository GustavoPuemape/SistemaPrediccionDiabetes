# predictor/serializers.py

from rest_framework import serializers
from .models import Prediction


class PredictionInputSerializer(serializers.Serializer):

    # =========================================================
    # DATOS DE ENTRADA
    # =========================================================

    age = serializers.FloatField(
        min_value=0,
        max_value=120,
        help_text="Edad del paciente en años"
    )

    pulse_rate = serializers.FloatField(
        min_value=30,
        max_value=200,
        help_text="Frecuencia cardíaca en latidos por minuto"
    )

    systolic_bp = serializers.FloatField(
        min_value=70,
        max_value=250,
        help_text="Presión arterial sistólica en mmHg"
    )

    diastolic_bp = serializers.FloatField(
        min_value=40,
        max_value=150,
        help_text="Presión arterial diastólica en mmHg"
    )

    glucose = serializers.FloatField(
        min_value=1.0,
        max_value=30.0,
        help_text="Nivel de glucosa en mmol/L"
    )

    height = serializers.FloatField(
        min_value=1.0,
        max_value=2.5,
        help_text="Altura del paciente en metros"
    )

    weight = serializers.FloatField(
        min_value=20,
        max_value=300,
        help_text="Peso del paciente en kilogramos"
    )

    bmi = serializers.FloatField(
        min_value=10,
        max_value=70,
        help_text="Índice de masa corporal"
    )

    # =========================================================
    # DATOS ADICIONALES
    # =========================================================
    family_diabetes = serializers.BooleanField(
        default=False,
        required=False,
        help_text="Historial familiar de diabetes"
    )

    hypertensive = serializers.BooleanField(
        default=False,
        required=False,
        help_text="Paciente hipertenso"
    )

    family_hypertension = serializers.BooleanField(
        default=False,
        required=False,
        help_text="Historial familiar de hipertensión"
    )

    cardiovascular_disease = serializers.BooleanField(
        default=False,
        required=False,
        help_text="Enfermedad cardiovascular"
    )

    stroke = serializers.BooleanField(
        default=False,
        required=False,
        help_text="Historial de derrame cerebral"
    )

    # =========================================================
    # VALIDACIONES
    # =========================================================

    def validate(self, data):
        # -----------------------------------------------------
        # 1. VALIDAR PRESIÓN ARTERIAL
        # -----------------------------------------------------

        if data['diastolic_bp'] >= data['systolic_bp']:
            raise serializers.ValidationError({
                'diastolic_bp': (
                    'La presión diastólica debe ser '
                    'menor que la presión sistólica.'
                )
            })


        calculated_bmi = (
            data['weight'] /
            (data['height'] ** 2)
        )

        if abs(
            calculated_bmi - data['bmi']
        ) > 2:

            data['bmi'] = calculated_bmi

        # -----------------------------------------------------
        # 3. VALIDAR RANGO FINAL DEL BMI
        # -----------------------------------------------------

        if not (
            10 <= data['bmi'] <= 70
        ):
            raise serializers.ValidationError({
                'bmi': (
                    'El BMI debe estar entre '
                    '10 y 70.'
                )
            })

        return data


# =============================================================
# OUTPUT
# =============================================================


class PredictionExplanationItemSerializer(serializers.Serializer):
    feature = serializers.CharField()
    condition = serializers.CharField()
    weight = serializers.FloatField()
    effect = serializers.ChoiceField(
        choices=['increases_risk', 'decreases_risk']
    )


class PredictionExplanationSerializer(serializers.Serializer):
    method = serializers.CharField()
    items = PredictionExplanationItemSerializer(many=True)
    fidelity = serializers.FloatField()
    note = serializers.CharField()

class PredictionOutputSerializer(serializers.Serializer):
    """
    Serializer para la respuesta de la predicción.
    """

    prediction = serializers.BooleanField(
        help_text="True = Predicción positiva, False = Predicción negativa"
    )

    probability = serializers.FloatField(
        min_value=0,
        max_value=1,
        help_text="Probabilidad de diabetes (0-1)"
    )

    probability_percentage = serializers.FloatField(
        min_value=0,
        max_value=100,
        help_text="Probabilidad de diabetes en porcentaje"
    )

    risk_level = serializers.CharField(
        help_text=(
            "Nivel de riesgo: "
            "BAJO, MODERADO, ALTO, MUY_ALTO"
        )
    )

    threshold = serializers.FloatField(
        min_value=0,
        max_value=1,
        help_text="Umbral utilizado para la clasificación"
    )

    message = serializers.CharField(
        help_text="Mensaje interpretativo de la predicción"
    )

    explanation = PredictionExplanationSerializer(
        required=False,
        help_text="Explicación local opcional generada por LIME"
    )


# =============================================================
# HISTORIAL COMPLETO
# =============================================================

class PredictionModelSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Prediction completo.
    """

    risk_level_display = serializers.CharField(
        source='get_risk_level',
        read_only=True
    )

    class Meta:
        model = Prediction
        fields = '__all__'
        read_only_fields = (
            'created_at',
            'updated_at'
        )


# =============================================================
# HISTORIAL SIMPLIFICADO
# =============================================================

class PredictionHistorySerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para el historial.
    """

    risk_level_display = serializers.CharField(
        source='get_risk_level',
        read_only=True
    )

    class Meta:
        model = Prediction

        fields = [
            'id',
            'age',
            'glucose',
            'bmi',
            'prediction',
            'probability',
            'risk_level',
            'risk_level_display',
            'created_at'
        ]

        read_only_fields = fields
