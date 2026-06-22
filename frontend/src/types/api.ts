export interface ApiErrorPayload {
  detail?: string | { msg: string; type?: string }[] | string[];
  message?: string;
  errors?: Record<string, string>;
}

export class ApiError extends Error {
  readonly status: number;
  readonly payload: ApiErrorPayload | undefined;

  constructor(message: string, status: number, payload?: ApiErrorPayload) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.payload = payload;
  }
}

export function extractApiErrorMessage(payload: ApiErrorPayload | undefined): string {
  if (!payload) return "An unexpected error occurred.";
  if (typeof payload.message === "string") return payload.message;
  if (typeof payload.detail === "string") return payload.detail;
  if (Array.isArray(payload.detail) && payload.detail.length > 0) {
    return payload.detail
      .map((item) => (typeof item === "string" ? item : item.msg))
      .filter(Boolean)
      .join(", ");
  }
  return "An unexpected error occurred.";
}
