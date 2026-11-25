import logging
import os
from pathlib import Path

import numpy as np
import pandas as pd
from django.conf import settings


logger = logging.getLogger(__name__)


EXPLANATION_FEATURES = {
    'age': 'Edad (años)',
    'pulse_rate': 'Frecuencia cardíaca (lpm)',
    'systolic_bp': 'Presión sistólica (mmHg)',
    'diastolic_bp': 'Presión diastólica (mmHg)',
    'glucose': 'Glucosa (mmol/L)',
    'height': 'Altura (m)',
    'weight': 'Peso (kg)',
    'bmi': 'Índice de masa corporal',
}


class PredictionExplainer:
    """Generates local explanations without changing the prediction pipeline."""

    def __init__(self, predictor, dataset_path=None):
        self.predictor = predictor
        self.explainer = None
        self.dataset_path = Path(
            dataset_path
            or os.environ.get(
                'LIME_DATASET_PATH',
                settings.BASE_DIR.parent / 'diabetes_balanced_full.csv',
            )
        )
        self._load()

    def _load(self):
        try:
            from lime.lime_tabular import LimeTabularExplainer

            dataset = pd.read_csv(self.dataset_path)
            columns = list(EXPLANATION_FEATURES)
            training_data = dataset[columns].dropna().to_numpy(dtype=float)

            if len(training_data) == 0:
                raise ValueError('The explainability dataset has no usable rows')

            self.explainer = LimeTabularExplainer(
                training_data,
                mode='classification',
                feature_names=list(EXPLANATION_FEATURES.values()),
                class_names=['Sin diabetes', 'Diabetes'],
                discretize_continuous=True,
                random_state=42,
            )
        except Exception as error:
            logger.warning('LIME explanation is unavailable: %s', error)
            self.explainer = None

    def _predict_original_inputs(self, rows):
        frames = []

        for row in rows:
            input_data = dict(
                zip(EXPLANATION_FEATURES, row)
            )
            frames.append(
                self.predictor.create_features(input_data)
            )

        features = pd.concat(frames, ignore_index=True)
        return self.predictor.model.predict_proba(features)

    def explain(self, input_data):
        """Explain one prediction in terms of the original clinical inputs."""
        if self.explainer is None:
            return None

        try:
            row = np.array([
                float(input_data[name])
                for name in EXPLANATION_FEATURES
            ])

            explanation = self.explainer.explain_instance(
                row,
                self._predict_original_inputs,
                labels=(1,),
                num_features=min(5, len(EXPLANATION_FEATURES)),
                num_samples=1000,
            )

            items = []
            for condition, weight in explanation.as_list(label=1):
                feature = next(
                    feature_name
                    for feature_name in EXPLANATION_FEATURES.values()
                    if feature_name in condition
                )
                items.append({
                    'feature': feature,
                    'condition': condition,
                    'weight': round(float(weight), 4),
                    'effect': (
                        'increases_risk'
                        if weight > 0
                        else 'decreases_risk'
                    ),
                })

            return {
                'method': 'LIME',
                'items': items,
                'fidelity': round(float(explanation.score), 4),
                'note': (
                    'Explicación local de apoyo. No representa causalidad '
                    'ni reemplaza la evaluación de un profesional de la salud.'
                ),
            }
        except Exception as error:
            logger.exception('Could not generate LIME explanation: %s', error)
            return None
