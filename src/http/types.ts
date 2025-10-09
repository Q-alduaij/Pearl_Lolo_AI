// src/http/types.ts
export type HttpMethod =
  | 'GET' | 'HEAD' | 'PUT' | 'DELETE'
  | 'POST' | 'PATCH' | 'OPTIONS';

export interface RetryBudget {
  /** Global operation budget in ms (includes retries & backoff) */
  totalMs: number; // e.g., 7000
  /** Max retry attempts (beyond the initial try) */
  maxRetries: number; // e.g., 1 or 2
  /** Base delay for backoff in ms */
  baseDelayMs: number; // e.g., 250
}

export interface RetryContext {
  startAt: number;     // t0 = Date.now()
  attempt: number;     // current attempt (0 = first try)
}

export interface TokenProvider {
  /** Return a valid access token (may trigger refresh internally) */
  getToken(): Promise<string>;
}
