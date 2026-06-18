import { env } from '../config/env';

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
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 15_000);

  try {
    const response = await fetch(`${env.apiBaseUrl}${path}`, {
      ...options,
      signal: controller.signal,
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
  } catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') {
      throw new ApiError(
        `Backend unreachable at ${env.apiBaseUrl}. Start the API on port 8000.`,
        0
      );
    }
    throw error;
  } finally {
    clearTimeout(timeout);
  }
}
