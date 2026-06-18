import { apiFetch } from './apiClient';
import type { ConversationDetailDto, ConversationSummaryDto } from '../types/api';

export function fetchConversations(token: string) {
  return apiFetch<ConversationSummaryDto[]>('/api/conversations', { method: 'GET' }, token);
}

export function fetchConversation(token: string, conversationId: string) {
  return apiFetch<ConversationDetailDto>(`/api/conversations/${conversationId}`, { method: 'GET' }, token);
}
