import { beforeEach, describe, expect, it, vi } from "vitest";
import type { User } from "@/types/auth";

vi.mock("@/api/authApi", () => ({
  authApi: {
    login: vi.fn(),
    logout: vi.fn(),
    getMe: vi.fn(),
  },
}));

import { authApi } from "@/api/authApi";
import { useAuthStore } from "./authStore";

const mockedAuthApi = vi.mocked(authApi, { deep: true });

function makeUser(overrides: Partial<User> = {}): User {
  return {
    id: 1,
    email: "user@example.com",
    first_name: "Test",
    last_name: "User",
    is_active: true,
    created_at: "2026/01/01 00:00",
    participant: { date_of_birth: "2000-01-01", gender: "MALE", tshirt_size: null, emergency_contact: "x" },
    organiser: null,
    admin: null,
    ...overrides,
  };
}

beforeEach(() => {
  vi.clearAllMocks();
  useAuthStore.setState({ user: null, isBootstrapping: true, isAuthenticated: false, role: null });
});

describe("useAuthStore.bootstrap", () => {
  it("populates the user on success", async () => {
    const user = makeUser();
    mockedAuthApi.getMe.mockResolvedValueOnce({ data: user } as never);

    await useAuthStore.getState().bootstrap();

    const state = useAuthStore.getState();
    expect(state.isAuthenticated).toBe(true);
    expect(state.user?.email).toBe("user@example.com");
    expect(state.role).toBe("participant");
    expect(state.isBootstrapping).toBe(false);
  });

  it("clears the user when getMe fails (not logged in)", async () => {
    mockedAuthApi.getMe.mockRejectedValueOnce(new Error("401"));

    await useAuthStore.getState().bootstrap();

    const state = useAuthStore.getState();
    expect(state.isAuthenticated).toBe(false);
    expect(state.user).toBeNull();
    expect(state.isBootstrapping).toBe(false);
  });
});

describe("useAuthStore.login", () => {
  it("logs in and populates the user", async () => {
    mockedAuthApi.login.mockResolvedValueOnce({ data: { message: "ok" } } as never);
    mockedAuthApi.getMe.mockResolvedValueOnce({ data: makeUser() } as never);

    await useAuthStore.getState().login("user@example.com", "password123");

    const state = useAuthStore.getState();
    expect(state.isAuthenticated).toBe(true);
    expect(state.user?.email).toBe("user@example.com");
  });

  it("propagates login failures without changing state", async () => {
    mockedAuthApi.login.mockRejectedValueOnce(new Error("Invalid credentials"));

    await expect(useAuthStore.getState().login("user@example.com", "wrong")).rejects.toThrow(
      "Invalid credentials",
    );
    expect(useAuthStore.getState().isAuthenticated).toBe(false);
  });
});

describe("useAuthStore.logout", () => {
  it("clears the user", async () => {
    useAuthStore.setState({ user: makeUser(), isAuthenticated: true, role: "participant" });
    mockedAuthApi.logout.mockResolvedValueOnce({ data: { message: "ok" } } as never);

    await useAuthStore.getState().logout();

    const state = useAuthStore.getState();
    expect(state.isAuthenticated).toBe(false);
    expect(state.user).toBeNull();
  });
});
