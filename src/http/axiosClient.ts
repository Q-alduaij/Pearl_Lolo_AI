// src/http/axiosClient.ts
import axios, { AxiosError, AxiosInstance, AxiosRequestConfig } from 'axios';
import { backoffDelay, isRetryableError, budgetExceeded } from './retryPolicy';
import type { HttpMethod, RetryBudget, RetryContext, TokenProvider } from './types';

/** Pin axios version in package.json: "axios": "1.7.4" */

const DEFAULT_BUDGET: RetryBudget = {
  totalMs: 7000,   // global operation budget
  maxRetries: 1,   // one retry beyond the initial attempt
  baseDelayMs: 250 // base delay for backoff
};

/** Create a scoped Axios instance with guardrails baked in */
export function createHttpClient(opts?: {
  baseURL?: string;
  defaultTimeoutMs?: number; // per-request timeout; default forbidden 0
  tokenProvider?: TokenProvider; // optional auth
  allowRetryOn?: Partial<Record<number, boolean>>; // override retryable status codes
}): AxiosInstance {
  const instance = axios.create({
    baseURL: opts?.baseURL,
    timeout: Math.max(1, opts?.defaultTimeoutMs ?? 5000), // forbid 0
    transitional: {
      // Clarify timeout errors in Axios 1.x
      clarifyTimeoutError: true,
    },
    // You can add default headers here, but avoid mutating global defaults.
  });

  // Track a single inflight refresh to avoid stampede (if using auth)
  let inflightRefresh: Promise<void> | null = null;

  /** REQUEST interceptor: add auth, trace headers, etc. */
  const reqId = instance.interceptors.request.use(
    async (config) => {
      // Attach auth token if a provider is present
      if (opts?.tokenProvider) {
        const token = await opts.tokenProvider.getToken();
        config.headers = {
          ...(config.headers ?? {}),
          Authorization: `Bearer ${token}`,
        };
      }

      // Attach a per-request AbortSignal timeout if not provided
      // (Node >=17.3) — keeps parity with axios timeout
      if (!config.signal && typeof AbortSignal !== 'undefined') {
        const perRequestMs = typeof config.timeout === 'number' ? config.timeout : 5000;
        config.signal = AbortSignal.timeout(perRequestMs);
      }

      // Initialize retry context on the config
      (config as any).__retryCtx = {
        startAt: Date.now(),
        attempt: 0,
      } as RetryContext;

      return config;
    },
    (error) => Promise.reject(error),
    // If you need sync behavior: { synchronous: true }
  );

  /** RESPONSE interceptor: handle auth-refresh + retry */
  const resId = instance.interceptors.response.use(
    (response) => response,
    async (error: AxiosError) => {
      const config = error.config as (AxiosRequestConfig & {
        __retryCtx?: RetryContext
        __retryCount?: number
        _retry?: boolean
      });

      // If no config, bail
      if (!config) throw error;

      const method = (config.method?.toUpperCase() ?? 'GET') as HttpMethod;
      const budget = DEFAULT_BUDGET;
      const ctx = config.__retryCtx ?? { startAt: Date.now(), attempt: 0 };

      // Optional: handle 401 -> refresh token flow (serialized)
      if (error.response?.status === 401 && opts?.tokenProvider) {
        if (!inflightRefresh) {
          inflightRefresh = (async () => {
            // Your refresh logic goes here, e.g. opts.tokenProvider.refresh()
            // Keep it short; propagate failure if refresh fails.
          })().finally(() => { inflightRefresh = null; });
        }
        try {
          await inflightRefresh;
          // Replay original request once after refresh
          return instance(config);
        } catch {
          // Refresh failed → surface original 401
          throw error;
        }
      }

      // Retry policy enforcement
      const attempt = (config.__retryCount ?? 0);
      const canRetry =
        attempt < budget.maxRetries &&
        !budgetExceeded(ctx, budget) &&
        isRetryableError(error, method);

      if (!canRetry) {
        // Annotate error with metadata for observability
        annotateAndThrow(error, attempt, ctx.startAt);
      }

      // Prepare next attempt
      const nextAttempt = attempt + 1;
      config.__retryCount = nextAttempt;
      ctx.attempt = nextAttempt;
      (config as any).__retryCtx = ctx;

      // Enforce global budget by capping backoff
      const delay = Math.min(
        backoffDelay(nextAttempt, budget.baseDelayMs),
        Math.max(0, budget.totalMs - (Date.now() - ctx.startAt) - 1)
      );

      if (delay > 0) await sleep(delay);

      return instance(config);
    }
  );

  // Expose a helper to eject interceptors on teardown (tests, hot reload, etc.)
  (instance as any).__ejectInterceptors = () => {
    instance.interceptors.request.eject(reqId);
    instance.interceptors.response.eject(resId);
  };

  return instance;
}

function sleep(ms: number) {
  return new Promise((r) => setTimeout(r, ms));
}

function annotateAndThrow(err: AxiosError, attempts: number, startAt: number): never {
  const elapsed = Date.now() - startAt;
  // Attach lightweight, redacted metadata
  (err as any).meta = {
    attempts,
    elapsedMs: elapsed,
    method: err.config?.method?.toUpperCase(),
    urlHost: safeHost(err.config?.url),
    status: err.response?.status,
    timeoutMs: err.config?.timeout,
  };
  throw err;
}

function safeHost(url?: string) {
  try {
    if (!url) return undefined;
    const u = new URL(url, 'http://placeholder.local'); // base for relative
    return u.host || undefined;
  } catch { return undefined; }
}
