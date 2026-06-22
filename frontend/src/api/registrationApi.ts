import { apiClient } from "./client";
import type { Registration, RegistrationCreate } from "@/types/registration";

export const registrationApi = {
  getMine() {
    return apiClient.get<Registration[]>("/api/registration/myregistrations");
  },

  getByRaceId(raceId: number) {
    return apiClient.get<Registration[]>("/api/registration/", {
      params: { race_id: raceId },
    });
  },

  create(payload: RegistrationCreate) {
    return apiClient.post<Registration>("/api/registration/", payload);
  },

  remove(registrationId: number) {
    return apiClient.delete<void>(`/api/registration/${registrationId}`);
  },
};
