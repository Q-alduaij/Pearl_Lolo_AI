// src/http/retryPolicy.ts
import type { HttpMethod, RetryBudget, RetryContext } from './types';
import type { AxiosError } from 'axios';

/** Idempotent methods allowed for retry */
export const IDEMPOTENT: Record<HttpMethod, boolean> = {
  GET: true, HEAD: true, PUT: true, DELETE: true,
  POST: false, PATCH: false, OPTIONS: false,
};

/** 5xx we allow retries on by default */
const RETRYABLE_5XX = new Set([502, 503, 504]);

/** Backoff with jitter (full jitter) */
export function backoffDelay(attempt: number, baseDelayMs: number): number {
  // attempt: 1 -> ~base; 2 -> ~2x base; add full jitter [0, delay)
  const delay = Math.pow(2, attempt - 1) * baseDelayMs;
  return Math.floor(Math.random() * Math.max(delay, baseDelayMs));
}

/** Is this error retryable under our policy? */
export function isRetryableError(err: AxiosError, method: HttpMethod): boolean {
  if (!IDEMPOTENT[method]) return false;

  const status = err.response?.status;
  const isNetwork = !!err.code && (
    err.code === 'ECONNRESET' ||
    err.code === 'ENOTFOUND' ||
    err.code === 'ETIMEDOUT' ||
    err.code === 'EAI_AGAIN' ||
    err.code === 'ECONNABORTED' // Axios timeout
  );

  if (isNetwork) return true;
  if (typeof status === 'number' && RETRYABLE_5XX.has(status)) return true;

  // Optional: 429/409 if you explicitly permit with backoff
  // if (status === 429 || status === 409) return true;

  return false;
}

/** Has this operation exceeded the global time budget? */
export function budgetExceeded(ctx: RetryContext, budget: RetryBudget): boolean {
  return (Date.now() - ctx.startAt) >= budget.totalMs;
}
