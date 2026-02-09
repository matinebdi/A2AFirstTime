// TripAdvisor service - now uses backend API via api.ts
// This file re-exports from api.ts for backward compatibility
export { tripadvisorApi } from './api';
export default { tripadvisorApi: () => import('./api').then(m => m.tripadvisorApi) };
