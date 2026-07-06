import { afterEach, describe, expect, it } from "vitest";
import { getCookie } from "./cookies";

afterEach(() => {
  document.cookie.split(";").forEach((cookie) => {
    const name = cookie.split("=")[0].trim();
    document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/`;
  });
});

describe("getCookie", () => {
  it("returns null when the cookie is not set", () => {
    expect(getCookie("csrf_token")).toBeNull();
  });

  it("reads a simple cookie value", () => {
    document.cookie = "csrf_token=abc123";
    expect(getCookie("csrf_token")).toBe("abc123");
  });

  it("decodes URL-encoded values", () => {
    document.cookie = `csrf_token=${encodeURIComponent("abc/123+xyz")}`;
    expect(getCookie("csrf_token")).toBe("abc/123+xyz");
  });

  it("finds the right cookie among several", () => {
    document.cookie = "access_token=irrelevant";
    document.cookie = "csrf_token=the-real-one";
    expect(getCookie("csrf_token")).toBe("the-real-one");
  });
});
