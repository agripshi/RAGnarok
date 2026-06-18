import { apiFetch } from './apiClient';
import type { FeedbackRequest } from '../types/api';

export function submitFeedback(token: string, request: FeedbackRequest) {
  return apiFetch<{ ok: boolean }>(
    '/api/feedback',
    { method: 'POST', body: JSON.stringify(request) },
    token
  );
}
