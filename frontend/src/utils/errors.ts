import { ApiError } from "@/types/api";

export function getErrorMessage(error: unknown, fallback = "Something went wrong.") {
  if (error instanceof ApiError) return error.message;
  if (error instanceof Error) return error.message;
  return fallback;
}

/** Use for mutation failures — surfaces backend detail for 4xx, generic copy for network/5xx. */
export function getMutationErrorMessage(
  error: unknown,
  fallback = "Something went wrong, please try again.",
) {
  if (error instanceof ApiError) {
    if (error.status === 0 || error.status >= 500) return fallback;
    return error.message;
  }
  if (error instanceof Error && error.message) return error.message;
  return fallback;
}

export function isApiError(error: unknown): error is ApiError {
  return error instanceof ApiError;
}

export function isServiceUnavailable(error: unknown): boolean {
  return (
    error instanceof ApiError &&
    (error.status === 0 || error.status === 404 || error.status >= 500)
  );
}
