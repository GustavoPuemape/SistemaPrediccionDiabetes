// src/app/features/prediction/prediction-stats/prediction-stats.component.ts

import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTooltipModule } from '@angular/material/tooltip';
import { Subject, takeUntil } from 'rxjs';
import { PredictionService } from '../../../core/services/prediction.service';
import { PredictionStats, RiskDistribution } from '../../../core/models/prediction.model';

/**
 * Fila de la distribución por nivel de riesgo.
 *
 * Usa el vocabulario abreviado de la tabla del historial
 * ("Bajo", "Moderado", …) con el color de la variable CSS
 * global que le corresponde.
 */
interface RiskDistributionRow {
  key: keyof RiskDistribution;
  label: string;
  cssVar: string;
}

@Component({
  selector: 'app-prediction-stats',
  standalone: true,
  imports: [
    CommonModule,
    RouterLink,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatProgressSpinnerModule,
    MatTooltipModule
  ],
  templateUrl: './prediction-stats.component.html',
  styleUrl: './prediction-stats.component.scss'
})
export class PredictionStatsComponent implements OnInit, OnDestroy {
  isLoading = false;
  errorMsg: string | null = null;
  stats: PredictionStats | null = null;

  readonly riskRows: RiskDistributionRow[] = [
    { key: 'bajo', label: 'Bajo', cssVar: 'var(--risk-low)' },
    { key: 'moderado', label: 'Moderado', cssVar: 'var(--risk-moderate)' },
    { key: 'alto', label: 'Alto', cssVar: 'var(--risk-high)' },
    { key: 'muy_alto', label: 'Muy Alto', cssVar: 'var(--risk-very-high)' }
  ];

  private destroy$ = new Subject<void>();

  constructor(private predictionService: PredictionService) {}

  ngOnInit(): void {
    this.loadStats();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  /**
   * Carga las estadísticas generales desde el backend.
   */
  loadStats(): void {
    this.isLoading = true;
    this.errorMsg = null;

    this.predictionService
      .getStats()
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (stats) => {
          this.stats = stats;
          this.isLoading = false;
        },
        error: (error) => {
          console.error('Error al cargar las estadísticas:', error);
          this.errorMsg =
            error?.message || 'No se pudieron cargar las estadísticas';
          this.stats = null;
          this.isLoading = false;
        }
      });
  }

  /**
   * Porcentaje de un nivel de riesgo sobre el total
   * (evita división por cero).
   */
  getRiskPercentage(count: number): number {
    if (!this.stats || this.stats.total_predictions === 0) {
      return 0;
    }
    return (count / this.stats.total_predictions) * 100;
  }
}
