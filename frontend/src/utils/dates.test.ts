import { describe, expect, it } from "vitest";
import { formatRaceDate, isBefore, isFutureDate, parseBackendDate } from "./dates";

describe("parseBackendDate", () => {
  it("parses the backend's yyyy/dd/MM HH:mm format", () => {
    const parsed = parseBackendDate("2026/25/12 18:30");
    expect(parsed).not.toBeNull();
    expect(parsed?.getFullYear()).toBe(2026);
    expect(parsed?.getMonth()).toBe(11); // December
    expect(parsed?.getDate()).toBe(25);
    expect(parsed?.getHours()).toBe(18);
    expect(parsed?.getMinutes()).toBe(30);
  });

  it("returns null for empty or missing input", () => {
    expect(parseBackendDate("")).toBeNull();
    expect(parseBackendDate(null)).toBeNull();
    expect(parseBackendDate(undefined)).toBeNull();
    expect(parseBackendDate("   ")).toBeNull();
  });

  it("falls back to native Date parsing for ISO strings", () => {
    const parsed = parseBackendDate("2026-01-15T10:00:00Z");
    expect(parsed).not.toBeNull();
  });

  it("returns null for garbage input", () => {
    expect(parseBackendDate("not-a-date-at-all")).toBeNull();
  });
});

describe("formatRaceDate", () => {
  it("returns the fallback for missing input", () => {
    expect(formatRaceDate(null)).toBe("—");
    expect(formatRaceDate(undefined, "N/A")).toBe("N/A");
  });

  it("formats a valid backend date into a human-readable string", () => {
    const formatted = formatRaceDate("2026/25/12 18:30");
    expect(formatted).not.toBe("—");
    expect(typeof formatted).toBe("string");
  });
});

describe("isFutureDate", () => {
  it("returns false for missing input", () => {
    expect(isFutureDate(null)).toBe(false);
  });

  it("returns true for a date far in the future", () => {
    expect(isFutureDate("2099/01/01 00:00")).toBe(true);
  });

  it("returns false for a date in the past", () => {
    expect(isFutureDate("2000/01/01 00:00")).toBe(false);
  });
});

describe("isBefore", () => {
  it("returns true when the first date precedes the second", () => {
    expect(isBefore("2026/01/01 00:00", "2026/02/01 00:00")).toBe(true);
  });

  it("returns false when the first date is after the second", () => {
    expect(isBefore("2026/02/01 00:00", "2026/01/01 00:00")).toBe(false);
  });

  it("returns false when either date is missing", () => {
    expect(isBefore(null, "2026/01/01 00:00")).toBe(false);
    expect(isBefore("2026/01/01 00:00", undefined)).toBe(false);
  });
});
