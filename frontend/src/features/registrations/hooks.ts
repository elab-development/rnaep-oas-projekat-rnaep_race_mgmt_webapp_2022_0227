import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { registrationApi } from "@/api/registrationApi";

export const registrationKeys = {
  all: ["registrations"] as const,
  mine: () => [...registrationKeys.all, "mine"] as const,
  byRace: (raceId: number) => [...registrationKeys.all, "race", raceId] as const,
};

export function useMyRegistrations() {
  return useQuery({
    queryKey: registrationKeys.mine(),
    queryFn: async () => (await registrationApi.getMine()).data,
  });
}

export function useRaceRegistrations(raceId: number, enabled = true) {
  return useQuery({
    queryKey: registrationKeys.byRace(raceId),
    queryFn: async () => (await registrationApi.getByRaceId(raceId)).data,
    enabled: enabled && raceId > 0,
  });
}

export function useCreateRegistration() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: registrationApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: registrationKeys.mine() });
      queryClient.invalidateQueries({ queryKey: registrationKeys.all });
    },
  });
}

export function useCancelRegistration() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: registrationApi.remove,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: registrationKeys.mine() });
      queryClient.invalidateQueries({ queryKey: registrationKeys.all });
    },
  });
}
