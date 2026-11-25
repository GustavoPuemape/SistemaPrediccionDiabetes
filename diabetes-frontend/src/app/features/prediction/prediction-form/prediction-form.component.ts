import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatDividerModule } from '@angular/material/divider';
import { Subject, takeUntil } from 'rxjs';
import { PredictionService } from '../../../core/services/prediction.service';
import { PredictionInput, PredictionResponse } from '../../../core/models/prediction.model';
import { PredictionResultComponent } from '../prediction-result/prediction-result.component';

@Component({
  selector: 'app-prediction-form',
  standalone: true,

  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatIconModule,
    MatProgressSpinnerModule,
    MatSnackBarModule,
    MatTooltipModule,
    MatDividerModule,
    PredictionResultComponent,
  ],

  templateUrl: './prediction-form.component.html',
  styleUrl: './prediction-form.component.scss',
})
export class PredictionFormComponent implements OnInit, OnDestroy {
  predictionForm!: FormGroup;
  isLoading = false;
  predictionResult: PredictionResponse | null = null;
  explanationLoading = false;
  viewingHistory = false;
  private destroy$ = new Subject<void>();

  constructor(
    private fb: FormBuilder,
    private predictionService: PredictionService,
    private snackBar: MatSnackBar,
    private route: ActivatedRoute,
    private router: Router,
  ) {}

  ngOnInit(): void {
    this.initForm();
    this.setupBMICalculation();

    const id = this.route.snapshot.paramMap.get('id');

    if (id) {
      this.loadFromHistory(Number(id));
    }
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  private initForm(): void {
    this.predictionForm = this.fb.group(
      {
        age: [null, [Validators.required, Validators.min(1), Validators.max(120)]],

        pulse_rate: [null, [Validators.required, Validators.min(30), Validators.max(200)]],

        systolic_bp: [null, [Validators.required, Validators.min(70), Validators.max(250)]],

        diastolic_bp: [null, [Validators.required, Validators.min(40), Validators.max(150)]],

        glucose: [null, [Validators.required, Validators.min(1), Validators.max(30)]],

        height: [null, [Validators.required, Validators.min(50), Validators.max(250)]],

        weight: [null, [Validators.required, Validators.min(20), Validators.max(300)]],

        bmi: [
          {
            value: 0,
            disabled: true,
          },
        ],
      },
      {
        validators: this.bloodPressureValidator,
      },
    );
  }

  private setupBMICalculation(): void {
    this.predictionForm
      .get('weight')
      ?.valueChanges.pipe(takeUntil(this.destroy$))
      .subscribe(() => {
        this.calculateBMI();
      });

    this.predictionForm
      .get('height')
      ?.valueChanges.pipe(takeUntil(this.destroy$))
      .subscribe(() => {
        this.calculateBMI();
      });

    this.calculateBMI();
  }

  private calculateBMI(): void {
    const weight = Number(this.predictionForm.get('weight')?.value);

    const heightCm = Number(this.predictionForm.get('height')?.value);

    if (weight > 0 && heightCm > 0) {
      const heightMeters = heightCm / 100;

      const bmi = weight / Math.pow(heightMeters, 2);

      this.predictionForm.get('bmi')?.setValue(Number(bmi.toFixed(6)), {
        emitEvent: false,
      });
    } else {
      this.predictionForm.get('bmi')?.setValue(0, {
        emitEvent: false,
      });
    }
  }

  private bloodPressureValidator(group: FormGroup): { [key: string]: boolean } | null {
    const systolic = Number(group.get('systolic_bp')?.value);

    const diastolic = Number(group.get('diastolic_bp')?.value);

    if (systolic && diastolic && diastolic >= systolic) {
      return {
        invalidBloodPressure: true,
      };
    }

    return null;
  }

  getErrorMessage(fieldName: string): string {
    const field = this.predictionForm.get(fieldName);

    if (field?.hasError('required')) {
      return 'Este campo es requerido';
    }

    if (field?.hasError('min')) {
      return `Valor mínimo: ${field.errors?.['min'].min}`;
    }

    if (field?.hasError('max')) {
      return `Valor máximo: ${field.errors?.['max'].max}`;
    }

    return '';
  }

  hasBloodPressureError(): boolean {
    return (
      this.predictionForm.hasError('invalidBloodPressure') &&
      this.predictionForm.get('systolic_bp')?.touched === true &&
      this.predictionForm.get('diastolic_bp')?.touched === true
    );
  }

  getBMIInterpretation(): string {
    const bmi = Number(this.predictionForm.get('bmi')?.value);

    if (!bmi) {
      return '';
    }

    if (bmi < 18.5) {
      return 'Bajo peso';
    }

    if (bmi < 25) {
      return 'Peso normal';
    }

    if (bmi < 30) {
      return 'Sobrepeso';
    }

    if (bmi < 35) {
      return 'Obesidad I';
    }

    if (bmi < 40) {
      return 'Obesidad II';
    }

    return 'Obesidad III';
  }

  getBMIColor(): string {
    const bmi = Number(this.predictionForm.get('bmi')?.value);

    if (!bmi) {
      return '#757575';
    }

    if (bmi < 18.5) {
      return '#FFC107';
    }

    if (bmi < 25) {
      return '#4CAF50';
    }

    if (bmi < 30) {
      return '#FF9800';
    }

    return '#F44336';
  }

  private loadFromHistory(id: number): void {
    this.isLoading = true;

    this.predictionService
      .getPredictionById(id)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (record) => {
          this.predictionForm.patchValue({
            age: record.age,

            pulse_rate: record.pulse_rate,

            systolic_bp: record.systolic_bp,

            diastolic_bp: record.diastolic_bp,

            glucose: record.glucose,

            height: Number((record.height * 100).toFixed(1)),

            weight: record.weight,
          });

           this.predictionResult = {
            success: true,

            prediction_id: record.id,

            created_at: record.created_at,

            result: {
              prediction: record.prediction,

              probability: record.probability,

              probability_percentage: Math.round(record.probability * 1000) / 10,

              risk_level: record.risk_level,
            },
           };

           this.explanationLoading = false;

          this.viewingHistory = true;

          this.isLoading = false;

          this.scrollToResult();
        },

        error: (error) => {
          console.error('❌ Error al cargar la predicción:', error);

          this.isLoading = false;

          this.snackBar.open(
            error?.message || 'No se pudo cargar la predicción seleccionada',
            'Cerrar',
            {
              duration: 5000,
              horizontalPosition: 'end',
              verticalPosition: 'top',
              panelClass: ['error-snackbar'],
            },
          );

          this.router.navigate(['/']);
        },
      });
  }

  onSubmit(): void {
    if (this.predictionForm.invalid) {
      this.markFormGroupTouched(this.predictionForm);

      this.snackBar.open('Por favor complete todos los campos requeridos correctamente', 'Cerrar', {
        duration: 3000,
        horizontalPosition: 'end',
        verticalPosition: 'top',
        panelClass: ['error-snackbar'],
      });

      return;
    }

    this.isLoading = true;

    this.predictionResult = null;
    this.explanationLoading = false;

    const formData = this.predictionForm.getRawValue();

    const heightMeters = Number(formData.height) / 100;

    const payload: PredictionInput = {
      age: Number(formData.age),

      pulse_rate: Number(formData.pulse_rate),

      systolic_bp: Number(formData.systolic_bp),

      diastolic_bp: Number(formData.diastolic_bp),

      glucose: Number(formData.glucose),

      height: Number(heightMeters.toFixed(8)),

      weight: Number(formData.weight),

      bmi: Number(formData.bmi),
    };

    console.log('📤 Payload enviado al backend:', payload);

    this.predictionService
      .predict(payload)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (response) => {
          console.log('📥 Respuesta del backend:', response);

          this.isLoading = false;

          this.predictionResult = response;
          this.explanationLoading = true;

          this.predictionService
            .explain(payload)
            .pipe(takeUntil(this.destroy$))
            .subscribe({
              next: (explanationResponse) => {
                if (this.predictionResult?.prediction_id !== response.prediction_id) {
                  return;
                }

                this.predictionResult = {
                  ...this.predictionResult,
                  result: {
                    ...this.predictionResult.result,
                    explanation: explanationResponse.explanation,
                  },
                };
                this.explanationLoading = false;
              },
              error: () => {
                this.explanationLoading = false;
              },
            });

          this.viewingHistory = false;

          this.scrollToResult();

          this.snackBar.open('Predicción realizada exitosamente', 'Cerrar', {
            duration: 3000,
            horizontalPosition: 'end',
            verticalPosition: 'top',
            panelClass: ['success-snackbar'],
          });
        },

        error: (error) => {
          console.error('❌ Error en predicción:', error);

          this.isLoading = false;

          const message =
            error?.error?.details ||
            error?.error?.error ||
            error?.message ||
            'Error al realizar la predicción';

          this.snackBar.open(message, 'Cerrar', {
            duration: 5000,
            horizontalPosition: 'end',
            verticalPosition: 'top',
            panelClass: ['error-snackbar'],
          });
        },
      });
  }

  private markFormGroupTouched(formGroup: FormGroup): void {
    Object.keys(formGroup.controls).forEach((key) => {
      formGroup.get(key)?.markAsTouched();
    });
  }

  private scrollToResult(): void {
    setTimeout(() => {
      const resultElement = document.querySelector('.result-section');

      if (resultElement) {
        resultElement.scrollIntoView({
          behavior: 'smooth',
          block: 'start',
        });
      }
    }, 100);
  }

  resetForm(): void {
    this.predictionForm.reset({
      age: null,

      pulse_rate: null,

      systolic_bp: null,

      diastolic_bp: null,

      // mmol/L
      glucose: null,

      // cm
      height: null,

      weight: null,

      bmi: null,
    });

    this.predictionResult = null;
    this.explanationLoading = false;

    this.calculateBMI();
  }

  newPrediction(): void {

    if (this.viewingHistory) {
      this.router.navigate(['/']);

      return;
    }

    this.predictionResult = null;
    this.explanationLoading = false;

    window.scrollTo({
      top: 0,
      behavior: 'smooth',
    });
  }
}
