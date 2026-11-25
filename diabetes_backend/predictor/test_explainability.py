from unittest.mock import patch

from django.test import TestCase
from rest_framework.test import APIClient

from .explainability import EXPLANATION_FEATURES, PredictionExplainer
from .utils import predictor


class PredictionExplainerTests(TestCase):
    def test_explains_the_original_clinical_inputs(self):
        explainer = PredictionExplainer(predictor)

        explanation = explainer.explain({
            'age': 55,
            'pulse_rate': 80,
            'systolic_bp': 140,
            'diastolic_bp': 90,
            'glucose': 8.5,
            'height': 1.70,
            'weight': 85,
            'bmi': 29.4,
        })

        self.assertIsNotNone(explanation)
        self.assertEqual(explanation['method'], 'LIME')
        self.assertGreaterEqual(len(explanation['items']), 1)
        self.assertLessEqual(len(explanation['items']), 5)
        self.assertTrue(
            set(item['feature'] for item in explanation['items']).issubset(
                set(EXPLANATION_FEATURES.values())
            )
        )

    @staticmethod
    def valid_input():
        return {
            'age': 55,
            'pulse_rate': 80,
            'systolic_bp': 140,
            'diastolic_bp': 90,
            'glucose': 8.5,
            'height': 1.70,
            'weight': 85,
            'bmi': 29.4,
        }

    @patch('predictor.views.get_prediction_explainer')
    def test_explanation_endpoint_is_optional(self, get_explainer):
        explanation = {
            'method': 'LIME',
            'items': [],
            'fidelity': 0.8,
            'note': 'Test explanation',
        }
        get_explainer.return_value.explain.return_value = explanation

        response = APIClient().post(
            '/api/predict/explanation/',
            self.valid_input(),
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['explanation'], explanation)

    @patch('predictor.views.predictor')
    def test_existing_prediction_response_does_not_require_explanation(self, predictor_mock):
        predictor_mock.predict.return_value = {
            'prediction': True,
            'probability': 0.8,
            'probability_percentage': 80.0,
            'risk_level': 'MUY_ALTO',
            'threshold': 0.6,
            'message': 'Test prediction',
        }

        response = APIClient().post(
            '/api/predict/',
            self.valid_input(),
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn('explanation', response.data['result'])
