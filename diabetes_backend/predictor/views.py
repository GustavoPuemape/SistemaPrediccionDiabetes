# predictor/views.py

import logging

from django.db import models
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Prediction
from .serializers import (
    PredictionInputSerializer,
    PredictionOutputSerializer,
    PredictionModelSerializer,
    PredictionHistorySerializer
)
from .utils import predictor


logger = logging.getLogger(__name__)


class PredictionAPIView(APIView):
    """
    Vista para realizar predicciones de diabetes.

    POST /api/predict/
    """

    def post(self, request):
        """
        Recibe los datos originales del paciente.

        Las features derivadas NO deben ser enviadas
        por el frontend. Son construidas internamente
        por predictor/utils.py.

        Request Body esperado:

        {
            "age": 45,
            "pulse_rate": 72,
            "systolic_bp": 140,
            "diastolic_bp": 90,
            "glucose": 200,
            "height": 170,
            "weight": 85,
            "bmi": 29.4,

            "family_diabetes": true,
            "hypertensive": true,
            "family_hypertension": false,
            "cardiovascular_disease": false,
            "stroke": false
        }
        """

        try:
            # =====================================================
            # 1. VALIDAR DATOS RECIBIDOS
            # =====================================================

            input_serializer = PredictionInputSerializer(
                data=request.data
            )

            if not input_serializer.is_valid():
                return Response(
                    {
                        'success': False,
                        'error': 'Datos de entrada inválidos',
                        'details': input_serializer.errors
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            validated_data = input_serializer.validated_data

            # =====================================================
            # 2. REALIZAR PREDICCIÓN
            # =====================================================
            #
            # utils.py se encarga de:
            #
            # datos originales
            #       ↓
            # feature engineering
            #       ↓
            # features.pkl
            #       ↓
            # model.pkl
            #
            # Por tanto, views.py NO construye features.
            #

            prediction_result = predictor.predict(
                validated_data
            )

            # =====================================================
            # 3. GUARDAR PREDICCIÓN EN BASE DE DATOS
            # =====================================================
            #
            # Los campos adicionales como family_diabetes,
            # hypertensive, etc. pueden seguir guardándose
            # para mantener el historial.
            #
            # Que se almacenen en la BD NO significa que
            # el nuevo modelo los utilice.
            #

            prediction_obj = Prediction.objects.create(
                age=validated_data['age'],
                pulse_rate=validated_data['pulse_rate'],
                systolic_bp=validated_data['systolic_bp'],
                diastolic_bp=validated_data['diastolic_bp'],
                glucose=validated_data['glucose'],
                height=validated_data['height'],
                weight=validated_data['weight'],
                bmi=validated_data['bmi'],

                # Datos históricos adicionales
                family_diabetes=validated_data.get(
                    'family_diabetes',
                    False
                ),
                hypertensive=validated_data.get(
                    'hypertensive',
                    False
                ),
                family_hypertension=validated_data.get(
                    'family_hypertension',
                    False
                ),
                cardiovascular_disease=validated_data.get(
                    'cardiovascular_disease',
                    False
                ),
                stroke=validated_data.get(
                    'stroke',
                    False
                ),

                # Resultado del nuevo modelo
                prediction=prediction_result['prediction'],
                probability=prediction_result['probability'],
                risk_level=prediction_result['risk_level']
            )

            # =====================================================
            # 4. VALIDAR FORMATO DE SALIDA
            # =====================================================

            output_serializer = PredictionOutputSerializer(
                data=prediction_result
            )

            output_serializer.is_valid(
                raise_exception=True
            )

            # =====================================================
            # 5. RESPUESTA
            # =====================================================

            response_data = {
                'success': True,
                'prediction_id': prediction_obj.id,
                'created_at': prediction_obj.created_at,
                'result': output_serializer.validated_data
            }

            logger.info(
                "Predicción exitosa: "
                f"ID={prediction_obj.id}, "
                f"Resultado={prediction_result['prediction']}, "
                f"Probabilidad={prediction_result['probability']:.4f}"
            )

            return Response(
                response_data,
                status=status.HTTP_200_OK
            )

        # =========================================================
        # ERRORES
        # =========================================================

        except ValueError as e:
            """
            Errores producidos por utils.py, por ejemplo:

            - Falta pulse_rate
            - Falta age
            - Falta glucose
            - Falta alguna entrada requerida
            """

            logger.error(
                f"Error de datos para predicción: {str(e)}"
            )

            return Response(
                {
                    'success': False,
                    'error': 'Datos insuficientes para realizar la predicción',
                    'details': str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:

            logger.exception(
                f"Error en predicción: {str(e)}"
            )

            return Response(
                {
                    'success': False,
                    'error': 'Error al procesar la predicción',
                    'details': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PredictionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para consultar el historial de predicciones.

    GET /api/predictions/
    GET /api/predictions/{id}/
    GET /api/predictions/stats/
    """

    queryset = Prediction.objects.all().order_by('-id')
    serializer_class = PredictionModelSerializer

    def get_serializer_class(self):
        """
        Utiliza un serializer simplificado para la lista.
        """

        if self.action == 'list':
            return PredictionHistorySerializer

        return PredictionModelSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Obtiene estadísticas generales.

        GET /api/predictions/stats/
        """

        try:

            total = Prediction.objects.count()

            diabetic = Prediction.objects.filter(
                prediction=True
            ).count()

            non_diabetic = total - diabetic

            # =====================================================
            # ESTADÍSTICAS
            # =====================================================

            if total > 0:

                avg_probability = (
                    Prediction.objects
                    .aggregate(
                        avg_prob=models.Avg(
                            'probability'
                        )
                    )
                    ['avg_prob']
                )

                risk_distribution = {
                    'bajo': Prediction.objects.filter(
                        risk_level='BAJO'
                    ).count(),

                    'moderado': Prediction.objects.filter(
                        risk_level='MODERADO'
                    ).count(),

                    'alto': Prediction.objects.filter(
                        risk_level='ALTO'
                    ).count(),

                    'muy_alto': Prediction.objects.filter(
                        risk_level='MUY_ALTO'
                    ).count(),
                }

            else:

                avg_probability = 0

                risk_distribution = {
                    'bajo': 0,
                    'moderado': 0,
                    'alto': 0,
                    'muy_alto': 0
                }

            # =====================================================
            # RESPUESTA
            # =====================================================

            stats_data = {
                'total_predictions': total,

                'diabetic_predictions': diabetic,

                'non_diabetic_predictions': non_diabetic,

                'diabetic_percentage': (
                    diabetic / total * 100
                    if total > 0
                    else 0
                ),

                'average_probability': (
                    round(avg_probability, 4)
                    if avg_probability is not None
                    else 0
                ),

                'risk_distribution': risk_distribution
            }

            return Response(
                stats_data,
                status=status.HTTP_200_OK
            )

        except Exception as e:

            logger.exception(
                f"Error al obtener estadísticas: {str(e)}"
            )

            return Response(
                {
                    'success': False,
                    'error': 'Error al obtener estadísticas',
                    'details': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
