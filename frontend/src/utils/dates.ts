import { parse, isValid } from "date-fns";

const BACKEND_DATETIME_FORMAT = "yyyy/dd/MM HH:mm";

function isNonEmptyString(value: unknown): value is string {
  return typeof value === "string" && value.trim().length > 0;
}

/** Backend serializes datetimes as YYYY/DD/MM HH:mm (day before month). */
export function parseBackendDate(value: string | null | undefined): Date | null {
  if (!isNonEmptyString(value)) return null;

  const trimmed = value.trim();

  try {
    const parsed = parse(trimmed, BACKEND_DATETIME_FORMAT, new Date());
    if (isValid(parsed)) return parsed;
  } catch {
    // date-fns can throw when the input shape is unexpected.
  }

  const iso = new Date(trimmed);
  return Number.isNaN(iso.getTime()) ? null : iso;
}

export function formatRaceDate(value: string | null | undefined, fallback = "—"): string {
  if (!isNonEmptyString(value)) return fallback;

  const date = parseBackendDate(value);
  if (!date) return fallback;

  return date.toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

export function isFutureDate(value: string | null | undefined): boolean {
  if (!isNonEmptyString(value)) return false;

  const date = parseBackendDate(value);
  if (!date) return false;

  return date.getTime() > Date.now();
}

export function isBefore(a: string | null | undefined, b: string | null | undefined): boolean {
  const dateA = isNonEmptyString(a) ? parseBackendDate(a) : null;
  const dateB = isNonEmptyString(b) ? parseBackendDate(b) : null;

  if (!dateA || !dateB) return false;

  return dateA.getTime() < dateB.getTime();
}
