import { apiClient } from "./client";
import type { Race, RaceCreate, RaceUpdate } from "@/types/race";

export const raceApi = {
  async list(): Promise<Race[]> {
    const response = await apiClient.get<Race[]>("/api/race/");
    return response.data;
  },

  getById(raceId: number) {
    return apiClient.get<Race>(`/api/race/${raceId}`);
  },

  create(payload: RaceCreate) {
    return apiClient.post<Race>("/api/race/", payload);
  },

  update(raceId: number, payload: RaceUpdate) {
    return apiClient.patch<Race>(`/api/race/${raceId}`, payload);
  },

  delete(raceId: number) {
    return apiClient.delete<void>(`/api/race/${raceId}`);
  },
};
