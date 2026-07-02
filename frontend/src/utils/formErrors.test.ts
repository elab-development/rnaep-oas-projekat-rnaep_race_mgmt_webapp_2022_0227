import { describe, expect, it, vi } from "vitest";
import { ApiError } from "@/types/api";
import { applyBackendFieldErrors, getBackendFieldErrors } from "./formErrors";

describe("getBackendFieldErrors", () => {
  it("returns null for non-ApiError input", () => {
    expect(getBackendFieldErrors(new Error("boom"))).toBeNull();
  });

  it("returns null when status is not 400", () => {
    const error = new ApiError("x", 401, { errors: { email: "bad" } });
    expect(getBackendFieldErrors(error)).toBeNull();
  });

  it("returns null when payload has no errors object", () => {
    const error = new ApiError("x", 400, {});
    expect(getBackendFieldErrors(error)).toBeNull();
  });

  it("normalizes string field errors", () => {
    const error = new ApiError("x", 400, { errors: { password: "Too short", email: "" } });
    expect(getBackendFieldErrors(error)).toEqual({ password: "Too short" });
  });
});

describe("applyBackendFieldErrors", () => {
  it("calls setError for each backend field error and returns true", () => {
    const setError = vi.fn();
    const error = new ApiError("x", 400, { errors: { password: "Too short" } });

    const applied = applyBackendFieldErrors(setError, error);

    expect(applied).toBe(true);
    expect(setError).toHaveBeenCalledWith("password", { type: "server", message: "Too short" });
  });

  it("returns false and does not call setError when there are no field errors", () => {
    const setError = vi.fn();
    const applied = applyBackendFieldErrors(setError, new Error("network down"));

    expect(applied).toBe(false);
    expect(setError).not.toHaveBeenCalled();
  });
});
