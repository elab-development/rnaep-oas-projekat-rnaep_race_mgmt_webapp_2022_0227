import { describe, expect, it } from "vitest";
import { ApiError } from "@/types/api";
import { getErrorMessage, getMutationErrorMessage, isApiError, isServiceUnavailable } from "./errors";

describe("getErrorMessage", () => {
  it("returns the ApiError message", () => {
    const error = new ApiError("Invalid credentials", 401);
    expect(getErrorMessage(error)).toBe("Invalid credentials");
  });

  it("returns a generic Error's message", () => {
    expect(getErrorMessage(new Error("boom"))).toBe("boom");
  });

  it("falls back for unknown error shapes", () => {
    expect(getErrorMessage("just a string")).toBe("Something went wrong.");
    expect(getErrorMessage("just a string", "Custom fallback")).toBe("Custom fallback");
  });
});

describe("getMutationErrorMessage", () => {
  it("surfaces the backend detail for 4xx errors", () => {
    const error = new ApiError("Email already registered", 400);
    expect(getMutationErrorMessage(error)).toBe("Email already registered");
  });

  it("uses the generic fallback for 5xx errors", () => {
    const error = new ApiError("Internal server error", 500);
    expect(getMutationErrorMessage(error)).toBe("Something went wrong, please try again.");
  });

  it("uses the generic fallback for network errors (status 0)", () => {
    const error = new ApiError("Unable to reach the server.", 0);
    expect(getMutationErrorMessage(error)).toBe("Something went wrong, please try again.");
  });
});

describe("isApiError", () => {
  it("identifies ApiError instances", () => {
    expect(isApiError(new ApiError("x", 400))).toBe(true);
    expect(isApiError(new Error("x"))).toBe(false);
  });
});

describe("isServiceUnavailable", () => {
  it("treats 404, 5xx, and network errors as service-unavailable", () => {
    expect(isServiceUnavailable(new ApiError("x", 404))).toBe(true);
    expect(isServiceUnavailable(new ApiError("x", 503))).toBe(true);
    expect(isServiceUnavailable(new ApiError("x", 0))).toBe(true);
  });

  it("does not treat ordinary 4xx errors as service-unavailable", () => {
    expect(isServiceUnavailable(new ApiError("x", 400))).toBe(false);
    expect(isServiceUnavailable(new ApiError("x", 403))).toBe(false);
  });
});
