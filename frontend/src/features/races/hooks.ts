import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { raceApi } from "@/api/raceApi";

export const raceKeys = {
  all: ["races"] as const,
  list: () => [...raceKeys.all, "list"] as const,
  detail: (id: number) => [...raceKeys.all, "detail", id] as const,
};

const raceQueryOptions = {
  staleTime: 0,
  gcTime: 0,
  refetchOnMount: "always" as const,
};

export function useRaces() {
  return useQuery({
    queryKey: raceKeys.list(),
    queryFn: () => raceApi.list(),
    ...raceQueryOptions,
  });
}

export function useRace(raceId: number) {
  return useQuery({
    queryKey: raceKeys.detail(raceId),
    queryFn: async () => (await raceApi.getById(raceId)).data,
    enabled: raceId > 0,
    ...raceQueryOptions,
  });
}

export function useCreateRace() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: raceApi.create,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: raceKeys.all }),
  });
}

export function useUpdateRace(raceId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: Parameters<typeof raceApi.update>[1]) =>
      raceApi.update(raceId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: raceKeys.detail(raceId) });
      queryClient.invalidateQueries({ queryKey: raceKeys.all });
    },
  });
}

export function useDeleteRace() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: raceApi.delete,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: raceKeys.all }),
  });
}
