// Simple in-memory rate limiter with circuit breaker

interface RateLimitState {
  requests: number[];
  disabled: boolean;
  disabledAt: number | null;
}

const state: RateLimitState = {
  requests: [],
  disabled: false,
  disabledAt: null,
};

// Configuration
const WINDOW_MS = 60 * 60 * 1000; // 1 hour window
const MAX_REQUESTS = parseInt(process.env.RATE_LIMIT_MAX || "50", 10);
const CIRCUIT_BREAKER_THRESHOLD = parseInt(
  process.env.CIRCUIT_BREAKER_THRESHOLD || "100",
  10
);

export interface RateLimitResult {
  allowed: boolean;
  remaining: number;
  resetAt: number;
  circuitBroken: boolean;
}

function cleanOldRequests(): void {
  const cutoff = Date.now() - WINDOW_MS;
  state.requests = state.requests.filter((ts) => ts > cutoff);
}

export function checkRateLimit(): RateLimitResult {
  // Check circuit breaker
  if (state.disabled) {
    return {
      allowed: false,
      remaining: 0,
      resetAt: state.disabledAt ? state.disabledAt + WINDOW_MS : Date.now(),
      circuitBroken: true,
    };
  }

  cleanOldRequests();

  const currentCount = state.requests.length;
  const remaining = Math.max(0, MAX_REQUESTS - currentCount);
  const oldestRequest = state.requests[0] || Date.now();
  const resetAt = oldestRequest + WINDOW_MS;

  // Check if circuit breaker should trip
  if (currentCount >= CIRCUIT_BREAKER_THRESHOLD) {
    state.disabled = true;
    state.disabledAt = Date.now();
    console.error(
      `🚨 Circuit breaker tripped at ${currentCount} requests`
    );
    return {
      allowed: false,
      remaining: 0,
      resetAt: Date.now() + WINDOW_MS,
      circuitBroken: true,
    };
  }

  if (currentCount >= MAX_REQUESTS) {
    return {
      allowed: false,
      remaining: 0,
      resetAt,
      circuitBroken: false,
    };
  }

  return {
    allowed: true,
    remaining: remaining - 1,
    resetAt,
    circuitBroken: false,
  };
}

export function recordRequest(): void {
  state.requests.push(Date.now());
}

export function resetCircuitBreaker(): void {
  state.disabled = false;
  state.disabledAt = null;
  state.requests = [];
  console.log("✅ Circuit breaker reset");
}

export function getStatus(): {
  requestsInWindow: number;
  maxRequests: number;
  circuitBroken: boolean;
} {
  cleanOldRequests();
  return {
    requestsInWindow: state.requests.length,
    maxRequests: MAX_REQUESTS,
    circuitBroken: state.disabled,
  };
}

