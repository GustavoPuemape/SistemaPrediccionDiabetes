// src/app/features/prediction/prediction-result/prediction-result.component.ts
import {
  Component,
  Input,
  Output,
  EventEmitter,
  OnInit,
  ViewChild,
  ElementRef,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatDividerModule } from '@angular/material/divider';
import { MatChipsModule } from '@angular/material/chips';
import {
  PredictionInput,
  PredictionResponse,
  RISK_LEVELS,
} from '../../../core/models/prediction.model';
import { Chart, registerables } from 'chart.js';

Chart.register(...registerables);

@Component({
  selector: 'app-prediction-result',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatProgressBarModule,
    MatDividerModule,
    MatChipsModule,
  ],
  templateUrl: './prediction-result.component.html',
  styleUrls: ['./prediction-result.component.scss'],
})
export class PredictionResultComponent implements OnInit {
  @Input() predictionData!: PredictionResponse;
  @Input() patientData?: PredictionInput;
  @Output() newPrediction = new EventEmitter<void>();
  @ViewChild('chartCanvas') chartCanvas!: ElementRef<HTMLCanvasElement>;

  chart?: Chart;
  riskInfo = RISK_LEVELS;

  ngOnInit(): void {
    // Crear gráfico después de que la vista esté inicializada
    setTimeout(() => this.createChart(), 100);
  }

  ngOnDestroy(): void {
    if (this.chart) {
      this.chart.destroy();
    }
  }

  /**
   * Obtiene la información del nivel de riesgo
   */
  getRiskLevelInfo() {
    return this.riskInfo[this.predictionData.result.risk_level];
  }

  /**
   * Obtiene el color del resultado
   */
  getResultColor(): string {
    return this.getRiskLevelInfo().color;
  }

  /**
   * Obtiene el ícono del resultado
   */
  getResultIcon(): string {
    return this.getRiskLevelInfo().icon;
  }

  /**
   * Crea el gráfico de probabilidad
   */
  private createChart(): void {
    if (!this.chartCanvas) return;

    const ctx = this.chartCanvas.nativeElement.getContext('2d');
    if (!ctx) return;

    const probability = this.predictionData.result.probability_percentage;
    const remaining = 100 - probability;

    this.chart = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: ['Probabilidad de Diabetes', 'Probabilidad de No Diabetes'],
        datasets: [
          {
            data: [probability, remaining],
            backgroundColor: [this.getResultColor(), '#e0e0e0'],
            borderWidth: 0,
            hoverOffset: 10,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        cutout: '70%',
        plugins: {
          legend: {
            display: false,
          },
          tooltip: {
            callbacks: {
              label: (context) => {
                return `${context.label}: ${context.parsed.toFixed(1)}%`;
              },
            },
          },
        },
      },
    });
  }

  /**
   * Emite evento para nueva predicción
   */
  onNewPrediction(): void {
    this.newPrediction.emit();
  }

  /**
   * Imprime el resultado
   */
  printResult(): void {
    document.body.classList.add('printing-result');
    window.addEventListener('afterprint', () => document.body.classList.remove('printing-result'), {
      once: true,
    });
    window.print();
  }
}
