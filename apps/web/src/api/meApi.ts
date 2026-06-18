import { apiFetch } from './apiClient';
import type { MeResponse } from '../types/api';

export function fetchMe(token: string) {
  return apiFetch<MeResponse>('/api/me', { method: 'GET' }, token);
}
