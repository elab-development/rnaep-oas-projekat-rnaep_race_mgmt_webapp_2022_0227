import { describe, expect, it } from "vitest";
import { isOrganiser, isParticipant, resolveUserRole } from "./auth";
import type { User } from "./auth";

function makeUser(overrides: Partial<User> = {}): User {
  return {
    id: 1,
    email: "user@example.com",
    first_name: "Test",
    last_name: "User",
    is_active: true,
    created_at: "2026/01/01 00:00",
    participant: null,
    organiser: null,
    admin: null,
    ...overrides,
  };
}

describe("resolveUserRole", () => {
  it("prioritizes admin over organiser and participant", () => {
    const user = makeUser({
      admin: { admin_level: 1 },
      organiser: { organization_name: "X", website: null, description: "d", is_verified: true },
      participant: { date_of_birth: "2000-01-01", gender: "MALE", tshirt_size: null, emergency_contact: "x" },
    });
    expect(resolveUserRole(user)).toBe("admin");
  });

  it("prioritizes organiser over participant", () => {
    const user = makeUser({
      organiser: { organization_name: "X", website: null, description: "d", is_verified: true },
      participant: { date_of_birth: "2000-01-01", gender: "MALE", tshirt_size: null, emergency_contact: "x" },
    });
    expect(resolveUserRole(user)).toBe("organiser");
  });

  it("returns participant when only a participant profile exists", () => {
    const user = makeUser({
      participant: { date_of_birth: "2000-01-01", gender: "FEMALE", tshirt_size: "M", emergency_contact: "x" },
    });
    expect(resolveUserRole(user)).toBe("participant");
  });

  it("falls back to user when no role profile exists", () => {
    expect(resolveUserRole(makeUser())).toBe("user");
  });
});

describe("isOrganiser / isParticipant", () => {
  it("treats admins as both organiser and participant", () => {
    const admin = makeUser({ admin: { admin_level: 1 } });
    expect(isOrganiser(admin)).toBe(true);
    expect(isParticipant(admin)).toBe(true);
  });

  it("returns false for null/undefined users", () => {
    expect(isOrganiser(null)).toBe(false);
    expect(isParticipant(undefined)).toBe(false);
  });

  it("distinguishes organiser-only from participant-only users", () => {
    const organiser = makeUser({
      organiser: { organization_name: "X", website: null, description: "d", is_verified: true },
    });
    expect(isOrganiser(organiser)).toBe(true);
    expect(isParticipant(organiser)).toBe(false);
  });
});
