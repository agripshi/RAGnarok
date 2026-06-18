import { apiFetch } from './apiClient';
import type { ChatRequest, ChatResponse } from '../types/api';

export { ApiError } from './apiClient';

export function sendChatMessage(token: string, request: ChatRequest) {
  return apiFetch<ChatResponse>(
    '/api/chat',
    { method: 'POST', body: JSON.stringify(request) },
    token
  );
}
