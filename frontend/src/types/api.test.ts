import { describe, expect, it } from "vitest";
import { ApiError, extractApiErrorMessage } from "./api";

describe("extractApiErrorMessage", () => {
  it("returns a default message when payload is missing", () => {
    expect(extractApiErrorMessage(undefined)).toBe("An unexpected error occurred.");
  });

  it("prefers the message field", () => {
    expect(extractApiErrorMessage({ message: "Custom message" })).toBe("Custom message");
  });

  it("falls back to a string detail field", () => {
    expect(extractApiErrorMessage({ detail: "Not found" })).toBe("Not found");
  });

  it("joins a list of validation error details", () => {
    const payload = { detail: [{ msg: "field required" }, { msg: "too short" }] };
    expect(extractApiErrorMessage(payload)).toBe("field required, too short");
  });

  it("returns the generic message for an unrecognized payload shape", () => {
    expect(extractApiErrorMessage({})).toBe("An unexpected error occurred.");
  });
});

describe("ApiError", () => {
  it("carries status and payload", () => {
    const error = new ApiError("Bad request", 400, { message: "Bad request" });
    expect(error.status).toBe(400);
    expect(error.message).toBe("Bad request");
    expect(error.payload?.message).toBe("Bad request");
    expect(error.name).toBe("ApiError");
  });
});
