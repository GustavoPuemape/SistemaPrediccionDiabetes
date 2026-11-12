# predictor/utils.py

import numpy as np
import pandas as pd
import joblib
import os
from django.conf import settings


class DiabetesPredictor:
    def __init__(self):
        self.model = None
        self.threshold = None
        self.features = None
        self.load_model()

    def load_model(self):
        """Carga modelo, umbral y features."""

        try:
            models_path = os.path.join(
                settings.BASE_DIR,
                'predictor',
                'models'
            )

            model_path = os.path.join(
                models_path,
                'model.pkl'
            )

            threshold_path = os.path.join(
                models_path,
                'threshold.npy'
            )

            features_path = os.path.join(
                models_path,
                'features.pkl'
            )

            # Cargar modelo
            self.model = joblib.load(model_path)

            # Cargar umbral
            self.threshold = float(
                np.load(threshold_path)
            )

            # Cargar features
            self.features = list(
                joblib.load(features_path)
            )

            print("✅ Modelo cargado exitosamente")
            print(
                f"✅ Umbral óptimo: "
                f"{self.threshold:.4f}"
            )

            print(
                f"✅ Features cargadas: "
                f"{len(self.features)}"
            )

            print(
                f"✅ Features: "
                f"{self.features}"
            )

        except Exception as e:
            print(
                f"❌ Error al cargar el modelo: "
                f"{str(e)}"
            )
            raise

    def safe_div(self, a, b):
        """División segura."""

        return a / (b + 1e-6)

    def feature_engineering(self, data):
        """
        Debe coincidir con el feature engineering
        utilizado durante el entrenamiento.
        """

        required_inputs = [
            'age',
            'pulse_rate',
            'systolic_bp',
            'diastolic_bp',
            'glucose',
            'height',
            'weight',
            'bmi'
        ]

        missing = [
            field
            for field in required_inputs
            if field not in data
        ]

        if missing:
            raise ValueError(
                f"Faltan campos requeridos: {missing}"
            )

        df = pd.DataFrame([data])

        # ==========================
        # CONVERSIÓN DE TIPOS
        # ==========================

        numeric_cols = [
            'age',
            'pulse_rate',
            'systolic_bp',
            'diastolic_bp',
            'glucose',
            'height',
            'weight',
            'bmi'
        ]

        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(
                    df[col],
                    errors='coerce'
                )

        binary_cols = [
            'family_diabetes',
            'hypertensive',
            'family_hypertension',
            'cardiovascular_disease',
            'stroke'
        ]

        for c in binary_cols:
            if c in df.columns:
                df[c] = pd.to_numeric(
                    df[c],
                    errors='coerce'
                ).fillna(0).astype(int)

        # ==========================
        # FEATURE ENGINEERING
        # ==========================

        df['mean_bp'] = (
            df['systolic_bp'] +
            2 * df['diastolic_bp']
        ) / 3

        df['bp_ratio'] = self.safe_div(
            df['systolic_bp'],
            df['diastolic_bp']
        )

        df['glucose_bmi_ratio'] = self.safe_div(
            df['glucose'],
            df['bmi']
        )

        df['age_bmi_interaction'] = (
            df['age'] *
            df['bmi']
        )

        df['weight_height_ratio'] = self.safe_div(
            df['weight'],
            df['height']
        )

        df['pulse_age_ratio'] = self.safe_div(
            df['pulse_rate'],
            df['age']
        )

        df['metabolic_risk_index'] = (
            df['glucose'] *
            df['bmi'] *
            df['mean_bp']
        ) / 10000

        df['pressure_glucose_index'] = self.safe_div(
            df['mean_bp'],
            df['glucose']
        )

        df['pulse_pressure'] = (
            df['systolic_bp'] -
            df['diastolic_bp']
        )

        df['bmi_squared'] = (
            df['bmi'] ** 2
        )

        df['glucose_squared'] = (
            df['glucose'] ** 2
        )

        df['risk_score'] = (
            df['glucose'] * 0.45 +
            df['bmi'] * 0.25 +
            df['age'] * 0.15 +
            df['mean_bp'] * 0.15
        )

        # Igual que durante entrenamiento
        df = df.fillna(
            df.median(
                numeric_only=True
            )
        )

        return df

    def create_features(self, data):
        """
        Crea todas las features y posteriormente
        selecciona exactamente las que necesita
        el nuevo modelo.
        """

        df = self.feature_engineering(data)

        # El modelo no necesita diabetic durante
        # una predicción.
        X = df.drop(
            columns=['diabetic'],
            errors='ignore'
        )

        # Utilizar exactamente las features
        # guardadas durante el entrenamiento.
        X = X[self.features]

        return X

    def predict(self, input_data):
        """Realiza la predicción."""

        try:

            if (
                self.model is None or
                self.threshold is None or
                self.features is None
            ):
                raise ValueError(
                    "Modelo, umbral o features "
                    "no cargados correctamente"
                )

            # Crear features
            X = self.create_features(
                input_data
            )

            # Probabilidad
            probability = (
                self.model
                .predict_proba(X)[0, 1]
            )

            # Aplicar threshold
            prediction = int(
                probability >= self.threshold
            )

            # Nivel de riesgo
            risk_level = (
                self.calculate_risk_level(
                    probability
                )
            )

            return {
                'prediction': bool(prediction),
                'probability': float(
                    probability
                ),
                'probability_percentage': float(
                    probability * 100
                ),
                'risk_level': risk_level,
                'threshold': float(
                    self.threshold
                ),
                'message': self.get_message(
                    prediction,
                    probability,
                    risk_level
                )
            }

        except Exception as e:

            print(
                f"❌ Error en predicción: "
                f"{str(e)}"
            )

            raise

    def calculate_risk_level(self, probability):

        if probability < 0.25:
            return 'BAJO'

        elif probability < 0.50:
            return 'MODERADO'

        elif probability < 0.75:
            return 'ALTO'

        else:
            return 'MUY_ALTO'

    def get_message(
        self,
        prediction,
        probability,
        risk_level
    ):

        risk_messages = {

            'BAJO':
                'El modelo indica un riesgo bajo de diabetes. Mantén un estilo de vida saludable.',

            'MODERADO':
                'El modelo indica un riesgo moderado de diabetes. Se recomienda consultar con un médico y realizar chequeos regulares.',

            'ALTO':
                'El modelo indica un riesgo alto de diabetes. Es importante consultar con un médico especialista pronto.',

            'MUY_ALTO':
                'El modelo indica un riesgo muy alto de diabetes. Se recomienda consultar con un médico especialista de inmediato.'
        }

        if prediction == 1:

            base_message = (
                "⚠️ **PREDICCIÓN POSITIVA**: "
                "El modelo predice que existe diabetes. "
            )

        else:

            base_message = (
                "✅ **PREDICCIÓN NEGATIVA**: "
                "El modelo predice que NO existe diabetes. "
            )

        return (
            base_message +
            risk_messages.get(
                risk_level,
                ''
            )
        )


# Instancia global
predictor = DiabetesPredictor()