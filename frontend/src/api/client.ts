import axios, { type AxiosError } from "axios";
import { ApiError, extractApiErrorMessage, type ApiErrorPayload } from "@/types/api";

/**
 * NOTE: Real UserService sets an httponly `access_token` cookie on login.
 * We use withCredentials (not Bearer/localStorage) to match the deployed backend.
 * TODO: If backend adds token-in-body responses, add optional Bearer interceptor.
 */
export const apiClient = axios.create({
  baseURL: import.meta.env.DEV ? "" : import.meta.env.VITE_API_BASE_URL || "",
  withCredentials: true,
  timeout: 30_000,
  headers: {
    Accept: "application/json",
    "Content-Type": "application/json",
  },
});

let onUnauthorized: (() => void) | null = null;

export function setUnauthorizedHandler(handler: () => void) {
  onUnauthorized = handler;
}

const AUTH_ATTEMPT_PATHS = ["/api/users/auth/login", "/api/users/auth/register"];

function isAuthAttemptRequest(url: string | undefined): boolean {
  if (!url) return false;
  return AUTH_ATTEMPT_PATHS.some((path) => url.includes(path));
}

apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ApiErrorPayload>) => {
    const normalized = error.response
      ? new ApiError(
          extractApiErrorMessage(error.response.data),
          error.response.status,
          error.response.data,
        )
      : new ApiError("Unable to reach the server.", 0);

    if (
      normalized.status === 401 &&
      onUnauthorized &&
      !isAuthAttemptRequest(error.config?.url)
    ) {
      onUnauthorized();
    }

    return Promise.reject(normalized);
  },
);
