import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import { useQueries } from "@tanstack/react-query";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { EmptyState } from "@/components/ui/EmptyState";
import { Modal } from "@/components/ui/Modal";
import { RaceFetchError } from "@/components/races/RaceFetchError";
import { RaceListSkeleton } from "@/components/ui/Skeleton";
import { registrationApi } from "@/api/registrationApi";
import { registrationKeys } from "@/features/registrations/hooks";
import { useDeleteRace, useRaces } from "@/features/races/hooks";
import { useAuth } from "@/hooks/useAuth";
import { formatRaceDate } from "@/utils/dates";
import { getErrorMessage, getMutationErrorMessage } from "@/utils/errors";

export function OrganiserDashboardPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const { data: races, isLoading, error, refetch, isFetching } = useRaces();
  const deleteRace = useDeleteRace();
  const [pendingDeleteId, setPendingDeleteId] = useState<number | null>(null);

  useEffect(() => {
    if (error) {
      toast.error(getErrorMessage(error, "Failed to load races."));
    }
  }, [error]);

  const myRaces = useMemo(
    () => races?.filter((race) => race.organiser_id === user?.id) ?? [],
    [races, user?.id],
  );

  const registrationQueries = useQueries({
    queries: myRaces.map((race) => ({
      queryKey: registrationKeys.byRace(race.id),
      queryFn: async () => (await registrationApi.getByRaceId(race.id)).data,
      enabled: !error && myRaces.length > 0,
    })),
  });

  const registrationCounts = useMemo(() => {
    const counts = new Map<number, number>();
    myRaces.forEach((race, index) => {
      const registrations = registrationQueries[index]?.data ?? [];
      counts.set(race.id, registrations.length);
    });
    return counts;
  }, [myRaces, registrationQueries]);

  async function confirmDelete() {
    if (!pendingDeleteId) return;
    try {
      await deleteRace.mutateAsync(pendingDeleteId);
      toast.success("Race deleted");
      setPendingDeleteId(null);
    } catch (caught) {
      toast.error(getMutationErrorMessage(caught));
    }
  }

  return (
    <div className="mx-auto max-w-6xl px-4 py-10 sm:px-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="font-display text-4xl font-black">Organiser Dashboard</h1>
          <p className="mt-2 text-slate-600">Manage races you created.</p>
        </div>
        <Link to="/organiser/races/new">
          <Button>Create Race</Button>
        </Link>
      </div>

      {isLoading ? <div className="mt-8"><RaceListSkeleton /></div> : null}

      {error ? (
        <div className="mt-8">
          <RaceFetchError
            error={error}
            onRetry={() => void refetch()}
            isRetrying={isFetching}
          />
        </div>
      ) : null}

      {!isLoading && !error && myRaces.length === 0 ? (
        <div className="mt-8">
          <EmptyState
            title="No races yet — be the first to create one!"
            description="Publish an upcoming OCR event and start accepting registrations."
            action={
              <Link to="/organiser/races/new">
                <Button>Create Race</Button>
              </Link>
            }
          />
        </div>
      ) : null}

      {!isLoading && !error && myRaces.length > 0 ? (
        <div className="mt-8 overflow-x-auto rounded-2xl border-2 border-slate-200 bg-white">
          <table className="min-w-full text-left text-sm">
            <thead className="bg-slate-100 text-xs font-bold uppercase text-slate-600">
              <tr>
                <th className="px-4 py-3">Race</th>
                <th className="px-4 py-3">Date</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Registrations</th>
                <th className="px-4 py-3">Actions</th>
              </tr>
            </thead>
            <tbody>
              {myRaces.map((race) => {
                const registered = registrationCounts.get(race.id) ?? 0;
                return (
                  <tr key={race.id} className="border-t border-slate-200">
                    <td className="px-4 py-4 font-semibold">{race.name}</td>
                    <td className="px-4 py-4">{formatRaceDate(race.date_time)}</td>
                    <td className="px-4 py-4">
                      <Badge label={race.status} tone={race.status} />
                    </td>
                    <td className="px-4 py-4">
                      {registered} / {race.max_participants}
                    </td>
                    <td className="px-4 py-4">
                      <div className="flex flex-wrap gap-2">
                        <Button
                          variant="secondary"
                          className="px-3 py-1.5 text-xs"
                          onClick={() => navigate(`/organiser/races/${race.id}/edit`)}
                        >
                          Edit
                        </Button>
                        <Button
                          variant="danger"
                          className="px-3 py-1.5 text-xs"
                          onClick={() => setPendingDeleteId(race.id)}
                        >
                          Delete
                        </Button>
                        <Button
                          variant="secondary"
                          className="px-3 py-1.5 text-xs"
                          onClick={() => navigate(`/organiser/races/${race.id}/registrations`)}
                        >
                          View Registrations
                        </Button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      ) : null}

      <Modal
        open={pendingDeleteId !== null}
        title="Delete race?"
        description="This permanently removes the race and cannot be undone."
        confirmLabel="Delete race"
        onConfirm={confirmDelete}
        onClose={() => setPendingDeleteId(null)}
      />
    </div>
  );
}
