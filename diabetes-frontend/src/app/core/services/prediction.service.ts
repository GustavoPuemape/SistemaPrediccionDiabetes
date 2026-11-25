import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError, BehaviorSubject } from 'rxjs';
import { catchError, tap } from 'rxjs/operators';
import { environment } from '../../../environments/environment';
import { 
  PredictionInput, 
  PredictionResponse, 
  PredictionHistoryResponse,
  PredictionStats,
  PredictionExplanationResponse,
} from '../models/prediction.model';

@Injectable({
  providedIn: 'root'
})
export class PredictionService {
  private apiUrl = environment.apiUrl;
  private lastPredictionSubject = new BehaviorSubject<PredictionResponse | null>(null);
  public lastPrediction$ = this.lastPredictionSubject.asObservable();

  constructor(private http: HttpClient) {}

  predict(data: PredictionInput): Observable<PredictionResponse> {
    return this.http.post<PredictionResponse>(`${this.apiUrl}/predict/`, data)
      .pipe(
        tap(response => this.lastPredictionSubject.next(response)),
        catchError(this.handleError)
      );
  }

  /**
   * Generates a local explanation without changing the saved prediction.
   */
  explain(data: PredictionInput): Observable<PredictionExplanationResponse> {
    return this.http
      .post<PredictionExplanationResponse>(`${this.apiUrl}/predict/explanation/`, data)
      .pipe(catchError(this.handleError));
  }

  getHistory(page: number = 1, pageSize: number = 10): Observable<PredictionHistoryResponse> {
    return this.http.get<PredictionHistoryResponse>(`${this.apiUrl}/predictions/?page=${page}&page_size=${pageSize}`)
      .pipe(catchError(this.handleError));
  }

  getPredictionById(id: number): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/predictions/${id}/`)
      .pipe(catchError(this.handleError));
  }

  getStats(): Observable<PredictionStats> {
    return this.http.get<PredictionStats>(`${this.apiUrl}/predictions/stats/`)
      .pipe(catchError(this.handleError));
  }

  calculateBMI(weight: number, height: number): number {
    if (weight && height && height > 0) {
      const heightInMeters = height / 100;
      return Math.round((weight / (heightInMeters * heightInMeters)) * 100) / 100;
    }
    return 0;
  }

  clearLastPrediction(): void {
    this.lastPredictionSubject.next(null);
  }

  private handleError(error: HttpErrorResponse) {
    let errorMessage = 'Ocurrió un error desconocido';
    
    if (error.error instanceof ErrorEvent) {
      // Error del lado del cliente
      errorMessage = `Error: ${error.error.message}`;
    } else {
      // Error del lado del servidor
      if (error.status === 0) {
        errorMessage = 'No se puede conectar con el servidor. Verifica que el backend esté en ejecución.';
      } else if (error.status === 400) {
        errorMessage = 'Datos inválidos. Por favor verifica la información ingresada.';
        if (error.error?.details) {
          const details = Object.values(error.error.details).flat().join(', ');
          errorMessage += ` Detalles: ${details}`;
        }
      } else if (error.status === 500) {
        errorMessage = 'Error en el servidor. Por favor contacta al administrador.';
      } else {
        errorMessage = `Error ${error.status}: ${error.message}`;
      }
    }

    console.error('Error completo:', error);
    return throwError(() => new Error(errorMessage));
  }
}
