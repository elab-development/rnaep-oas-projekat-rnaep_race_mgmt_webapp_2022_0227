import type { FieldValues, Path, UseFormSetError } from "react-hook-form";
import { ApiError } from "@/types/api";

export function getBackendFieldErrors(error: unknown): Record<string, string> | null {
  if (!(error instanceof ApiError) || error.status !== 400) return null;

  const errors = error.payload?.errors;
  if (!errors || typeof errors !== "object" || Array.isArray(errors)) return null;

  const normalized: Record<string, string> = {};
  for (const [field, message] of Object.entries(errors)) {
    if (typeof message === "string" && message.length > 0) {
      normalized[field] = message;
    }
  }

  return Object.keys(normalized).length > 0 ? normalized : null;
}

export function applyBackendFieldErrors<T extends FieldValues>(
  setError: UseFormSetError<T>,
  error: unknown,
): boolean {
  const fieldErrors = getBackendFieldErrors(error);
  if (!fieldErrors) return false;

  for (const [field, message] of Object.entries(fieldErrors)) {
    setError(field as Path<T>, { type: "server", message });
  }

  return true;
}
