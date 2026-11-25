import {
  Component,
  OnInit,
  OnDestroy,
  AfterViewInit,
  ViewChild
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { MatTableModule, MatTableDataSource } from '@angular/material/table';
import {
  MatPaginatorModule,
  MatPaginator,
  MatPaginatorIntl
} from '@angular/material/paginator';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatChipsModule } from '@angular/material/chips';
import { Subject, takeUntil } from 'rxjs';
import { PredictionService } from '../../../core/services/prediction.service';
import {
  PredictionHistory,
  RISK_LEVELS,
  RiskLevel,
  RiskLevelInfo
} from '../../../core/models/prediction.model';

/**
 * Etiquetas en español para MatPaginator.
 */
export function spanishPaginatorIntl(): MatPaginatorIntl {
  const intl = new MatPaginatorIntl();
  intl.itemsPerPageLabel = 'Elementos por página';
  intl.firstPageLabel = 'Primera página';
  intl.previousPageLabel = 'Página anterior';
  intl.nextPageLabel = 'Página siguiente';
  intl.lastPageLabel = 'Última página';
  intl.getRangeLabel = (page: number, pageSize: number, length: number): string => {
    if (length === 0 || pageSize === 0) {
      return `0 de ${length}`;
    }
    const from = page * pageSize + 1;
    const to = Math.min((page + 1) * pageSize, length);
    return `${from}–${to} de ${length}`;
  };
  return intl;
}

@Component({
  selector: 'app-prediction-history',
  standalone: true,
  providers: [
    { provide: MatPaginatorIntl, useFactory: spanishPaginatorIntl }
  ],
  imports: [
    CommonModule,
    MatTableModule,
    MatPaginatorModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatProgressSpinnerModule,
    MatSnackBarModule,
    MatTooltipModule,
    MatChipsModule
  ],
  templateUrl: './prediction-history.component.html',
  styleUrl: './prediction-history.component.scss'
})
export class PredictionHistoryComponent
  implements OnInit, AfterViewInit, OnDestroy {
  @ViewChild(MatPaginator) paginator!: MatPaginator;

  readonly displayedColumns: string[] = [
    'id',
    'created_at',
    'age',
    'glucose',
    'bmi',
    'probability',
    'prediction',
    'risk_level'
  ];

  readonly dataSource = new MatTableDataSource<PredictionHistory>([]);

  totalCount = 0;
  isLoading = false;
  hasError = false;

  private destroy$ = new Subject<void>();

  constructor(
    private predictionService: PredictionService,
    private snackBar: MatSnackBar,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.loadHistory();
  }

  ngAfterViewInit(): void {
    // Paginación en el cliente sobre la lista completa.
    this.dataSource.paginator = this.paginator;
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  /**
   * Carga el historial de predicciones.
   *
   * El backend actual no tiene paginación DRF configurada, por lo que
   * ignora page/page_size y devuelve un arreglo plano. Se pagina en el
   * cliente con MatPaginator. También soporta sobre paginado DRF
   * (results/count) si se habilita en el futuro.
   */
  loadHistory(): void {
    this.isLoading = true;
    this.hasError = false;

    this.predictionService
      .getHistory(1, 50)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (response) => {
          // Backend actual: arreglo plano. Futuro: sobre paginado DRF.
          const items: PredictionHistory[] = Array.isArray(response)
            ? response
            : response.results;

          this.dataSource.data = items;
          this.totalCount = items.length;
          this.isLoading = false;
        },
        error: (error) => {
          console.error('Error al cargar el historial:', error);

          this.isLoading = false;
          this.hasError = true;
          this.dataSource.data = [];
          this.totalCount = 0;

          this.snackBar.open(
            error?.message ||
              'No se pudo cargar el historial de predicciones',
            'Cerrar',
            {
              duration: 5000,
              horizontalPosition: 'end',
              verticalPosition: 'top',
              panelClass: ['error-snackbar']
            }
          );
        }
      });
  }

  /**
   * Obtiene la información del nivel de riesgo (color, icono, etiqueta).
   */
  getRiskInfo(level: RiskLevel): RiskLevelInfo {
    return RISK_LEVELS[level] ?? RISK_LEVELS['BAJO'];
  }

  /**
   * Convierte la probabilidad (0-1) a porcentaje para mostrarla.
   */
  getProbabilityPercentage(probability: number): number {
    return Math.round(probability * 1000) / 10;
  }

  /**
   * Navega al formulario de nueva predicción.
   */
  goToNewPrediction(): void {
    this.router.navigate(['/']);
  }

  /**
   * Abre el detalle de una predicción en el formulario
   * (prefill + tarjeta de resultado).
   */
  openPrediction(row: PredictionHistory): void {
    this.router.navigate(['/predict', row.id]);
  }
}
