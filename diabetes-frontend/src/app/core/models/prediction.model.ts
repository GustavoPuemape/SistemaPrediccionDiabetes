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

export interface PredictionHistoryPage {
  count: number;
  next: string | null;
  previous: string | null;
  results: PredictionHistory[];
}

export type PredictionHistoryResponse = PredictionHistory[] | PredictionHistoryPage;

export interface RiskDistribution {
  bajo: number;
  moderado: number;
  alto: number;
  muy_alto: number;
}

export interface PredictionStats {
  total_predictions: number;
  diabetic_predictions: number;
  non_diabetic_predictions: number;
  diabetic_percentage: number;
  average_probability: number;
  risk_distribution: RiskDistribution;
}
