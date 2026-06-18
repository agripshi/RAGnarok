import { env } from '../config/env';
import type { ChatRequest, ChatResponse } from '../types/api';

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
    public readonly payload?: unknown
  ) {
    super(message);
  }
}

export async function apiFetch<T>(path: string, options: RequestInit, token: string): Promise<T> {
  const response = await fetch(`${env.apiBaseUrl}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
      ...(options.headers ?? {}),
    },
  });

  if (!response.ok) {
    let payload: unknown = null;
    try {
      payload = await response.json();
    } catch {
      payload = null;
    }
    throw new ApiError(`API request failed: ${response.status}`, response.status, payload);
  }

  return response.json() as Promise<T>;
}

export function sendChatMessage(token: string, request: ChatRequest) {
  return apiFetch<ChatResponse>(
    '/api/chat',
    { method: 'POST', body: JSON.stringify(request) },
    token
  );
}
