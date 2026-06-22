import { create } from "zustand";
import { authApi } from "@/api/authApi";
import type { User } from "@/types/auth";
import { resolveUserRole } from "@/types/auth";

interface AuthState {
  user: User | null;
  isBootstrapping: boolean;
  isAuthenticated: boolean;
  role: ReturnType<typeof resolveUserRole> | null;
  bootstrap: () => Promise<void>;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  setUser: (user: User | null) => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isBootstrapping: true,
  isAuthenticated: false,
  role: null,

  setUser(user) {
    set({
      user,
      isAuthenticated: Boolean(user),
      role: user ? resolveUserRole(user) : null,
    });
  },

  async bootstrap() {
    set({ isBootstrapping: true });
    try {
      const response = await authApi.getMe();
      set({
        user: response.data,
        isAuthenticated: true,
        role: resolveUserRole(response.data),
        isBootstrapping: false,
      });
    } catch {
      set({
        user: null,
        isAuthenticated: false,
        role: null,
        isBootstrapping: false,
      });
    }
  },

  async login(email, password) {
    await authApi.login({ email, password });
    const response = await authApi.getMe();
    set({
      user: response.data,
      isAuthenticated: true,
      role: resolveUserRole(response.data),
    });
  },

  async logout() {
    await authApi.logout();
    set({ user: null, isAuthenticated: false, role: null });
  },
}));
