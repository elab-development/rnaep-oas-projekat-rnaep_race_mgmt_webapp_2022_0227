import { useAuthStore } from "@/store/authStore";
import { isOrganiser, isParticipant } from "@/types/auth";

export function useAuth() {
  const state = useAuthStore();
  return {
    ...state,
    isOrganiser: isOrganiser(state.user),
    isParticipant: isParticipant(state.user),
  };
}
