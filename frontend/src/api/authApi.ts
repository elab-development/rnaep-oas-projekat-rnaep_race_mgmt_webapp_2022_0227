import { apiClient } from "./client";
import type {
  LoginRequest,
  MessageResponse,
  OrganiserRegisterRequest,
  ParticipantRegisterRequest,
  User,
} from "@/types/auth";

const AUTH = "/api/users/auth";

export const authApi = {
  login(payload: LoginRequest) {
    return apiClient.post<MessageResponse>(`${AUTH}/login`, payload);
  },
  logout() {
    return apiClient.post<MessageResponse>(`${AUTH}/logout`);
  },
  registerParticipant(payload: ParticipantRegisterRequest) {
    return apiClient.post<User>(`${AUTH}/register/participant`, payload);
  },
  registerOrganiser(payload: OrganiserRegisterRequest) {
    return apiClient.post<User>(`${AUTH}/register/organiser`, payload);
  },
  getMe() {
    return apiClient.get<User>("/api/users/me");
  },
};
