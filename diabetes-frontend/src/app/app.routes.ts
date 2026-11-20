import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: '',
    title: 'Predecir | Sistema de Predicción de Diabetes',
    loadComponent: () =>
      import('./features/prediction/prediction-form/prediction-form.component').then(
        (m) => m.PredictionFormComponent
      )
  },
  {
    path: 'history',
    title: 'Historial | Sistema de Predicción de Diabetes',
    loadComponent: () =>
      import('./features/prediction/prediction-history/prediction-history.component').then(
        (m) => m.PredictionHistoryComponent
      )
  },
  {
    path: 'predict/:id',
    title: 'Detalle de Predicción | Sistema de Predicción de Diabetes',
    loadComponent: () =>
      import('./features/prediction/prediction-form/prediction-form.component').then(
        (m) => m.PredictionFormComponent
      )
  },
  {
    path: 'stats',
    title: 'Estadísticas | Sistema de Predicción de Diabetes',
    loadComponent: () =>
      import('./features/prediction/prediction-stats/prediction-stats.component').then(
        (m) => m.PredictionStatsComponent
      )
  },
  {
    path: '**',
    redirectTo: ''
  }
];
