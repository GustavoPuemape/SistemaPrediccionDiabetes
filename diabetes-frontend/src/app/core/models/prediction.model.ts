export interface PredictionInput {
  age: number;
  pulse_rate: number;
  systolic_bp: number;
  diastolic_bp: number;
  glucose: number;
  height: number;
  weight: number;
  bmi: number;
}

export interface PredictionResult {
  prediction: boolean;
  probability: number;
  probability_percentage: number;
  risk_level: RiskLevel;
  threshold?: number;
  message?: string;
  explanation?: PredictionExplanation;
}

export type ExplanationEffect = 'increases_risk' | 'decreases_risk';

export interface PredictionExplanationItem {
  feature: string;
  condition: string;
  weight: number;
  effect: ExplanationEffect;
}

export interface PredictionExplanation {
  method: string;
  items: PredictionExplanationItem[];
  fidelity: number;
  note: string;
}

export interface PredictionExplanationResponse {
  success: boolean;
  explanation: PredictionExplanation;
}

export interface PredictionResponse {
  success: boolean;
  prediction_id: number;
  created_at: string;
  result: PredictionResult;
}

export type RiskLevel = 'BAJO' | 'MODERADO' | 'ALTO' | 'MUY_ALTO';

export interface RiskLevelInfo {
  label: string;
  color: string;
  icon: string;
  description: string;
}

export const RISK_LEVELS: Record<RiskLevel, RiskLevelInfo> = {
  BAJO: {
    label: 'Riesgo Bajo',
    color: '#4CAF50',
    icon: 'check_circle',
    description: 'Bajo riesgo de diabetes. Mantén un estilo de vida saludable.',
  },
  MODERADO: {
    label: 'Riesgo Moderado',
    color: '#FFC107',
    icon: 'warning',
    description:
      'Riesgo moderado. Se recomienda consultar con un médico y realizar chequeos regulares.',
  },
  ALTO: {
    label: 'Riesgo Alto',
    color: '#FF9800',
    icon: 'error',
    description: 'Riesgo alto. Es importante consultar con un médico especialista pronto.',
  },
  MUY_ALTO: {
    label: 'Riesgo Muy Alto',
    color: '#F44336',
    icon: 'cancel',
    description:
      'Riesgo muy alto. Se recomienda consultar con un médico especialista de inmediato.',
  },
};

/**
 * Item del historial de predicciones.
 *
 * Coincide con PredictionHistorySerializer del backend:
 * id, age, glucose, bmi, prediction, probability,
 * risk_level, risk_level_display, created_at.
 */
export interface PredictionHistory {
  id: number;
  age: number;
  glucose: number;
  bmi: number;
  prediction: boolean;
  probability: number;
  risk_level: RiskLevel;
  risk_level_display: string;
  created_at: string;
}

/**
 * Forma paginada DRF (count/next/previous/results).
 *
 * El backend actual NO configura paginación DRF
 * (sin DEFAULT_PAGINATION_CLASS ni pagination_class en el ViewSet),
 * por lo que GET /api/predictions/ devuelve actualmente un arreglo
 * plano. Este tipo se mantiene para tolerar un sobre paginado
 * si se habilita la paginación en el backend en el futuro.
 */
export interface PredictionHistoryPage {
  count: number;
  next: string | null;
  previous: string | null;
  results: PredictionHistory[];
}

/**
 * Respuesta real de GET /api/predictions/: arreglo plano hoy,
 * o sobre paginado si el backend habilita paginación DRF.
 */
export type PredictionHistoryResponse = PredictionHistory[] | PredictionHistoryPage;

/**
 * Distribución de predicciones por nivel de riesgo.
 *
 * Claves en minúsculas, tal como las devuelve el backend
 * en la acción `stats` del ViewSet de predicciones.
 */
export interface RiskDistribution {
  bajo: number;
  moderado: number;
  alto: number;
  muy_alto: number;
}

/**
 * Estadísticas generales de predicciones.
 *
 * Coincide con la respuesta de la acción `stats` del backend
 * (GET /api/predictions/stats/): totales agregados, desglose
 * diabético/no diabético con su porcentaje, probabilidad
 * promedio (0-1) y distribución por nivel de riesgo.
 */
export interface PredictionStats {
  total_predictions: number;
  diabetic_predictions: number;
  non_diabetic_predictions: number;
  diabetic_percentage: number;
  average_probability: number;
  risk_distribution: RiskDistribution;
}
