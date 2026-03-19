// src/lib/errorHandler.ts
import { ApiError } from "./api";

export interface RateLimitInfo {
  isRateLimited: boolean;
  retryAfter: number | null; // seconds
  message: string;
}

export function parseRateLimitError(error: unknown): RateLimitInfo | null {
  if (!(error instanceof ApiError)) return null;

  // Check for 429 (Too Many Requests)
  if (error.status === 429) {
    const retryAfter = extractRetryAfter(error);
    return {
      isRateLimited: true,
      retryAfter,
      message: error.message || "Too many requests. Please wait before trying again.",
    };
  }

  return null;
}

function extractRetryAfter(error: ApiError): number | null {
  // Try to extract from payload
  if (typeof error.payload === "object" && error.payload !== null) {
    const payload = error.payload as any;
    
    // Check for retry_after field (common pattern)
    if (typeof payload.retry_after === "number") {
      return payload.retry_after;
    }
    
    // Check for detail message with time
    if (typeof payload.detail === "string") {
      const match = payload.detail.match(/try again in (\d+) seconds?/i);
      if (match) return parseInt(match[1], 10);
    }
  }

  // Default to 60 seconds if not specified
  return 60;
}

export function isNetworkError(error: unknown): boolean {
  return error instanceof ApiError && error.status === 0;
}

export function isForbiddenError(error: unknown): boolean {
  return error instanceof ApiError && error.status === 403;
}

export function isNotFoundError(error: unknown): boolean {
  return error instanceof ApiError && error.status === 404;
}

export function isServerError(error: unknown): boolean {
  return error instanceof ApiError && error.status >= 500 && error.status < 600;
}

export function getErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    return error.message;
  }
  if (error instanceof Error) {
    return error.message;
  }
  return String(error);
}

export function handleApiError(error: unknown): {
  message: string;
  shouldRedirect: boolean;
  redirectUrl?: string;
} {
  if (isForbiddenError(error)) {
    return {
      message: "Access denied. Please login to continue.",
      shouldRedirect: true,
      redirectUrl: "/login",
    };
  }

  if (isNotFoundError(error)) {
    return {
      message: "The requested resource was not found.",
      shouldRedirect: true,
      redirectUrl: "/404",
    };
  }

  if (isServerError(error)) {
    return {
      message: "A server error occurred. Please try again later.",
      shouldRedirect: false,
    };
  }

  if (isNetworkError(error)) {
    return {
      message: "Network error. Please check your connection.",
      shouldRedirect: false,
    };
  }

  return {
    message: getErrorMessage(error),
    shouldRedirect: false,
  };
}
