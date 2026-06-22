import { Link, Navigate, useParams } from "react-router-dom";
import { Badge } from "@/components/ui/Badge";
import { EmptyState } from "@/components/ui/EmptyState";
import { TableSkeleton } from "@/components/ui/Skeleton";
import { useRaceRegistrations } from "@/features/registrations/hooks";
import { useRace } from "@/features/races/hooks";
import { useAuth } from "@/hooks/useAuth";
import { formatRaceDate } from "@/utils/dates";
import { getMutationErrorMessage, isApiError, isServiceUnavailable } from "@/utils/errors";

function participantLabel(participantId: number) {
  return `Participant #${participantId}`;
}

export function OrganiserRaceRegistrationsPage() {
  const { id } = useParams();
  const raceId = Number(id);
  const { user } = useAuth();
  const { data: race, isLoading: raceLoading } = useRace(raceId);
  const { data: registrations, isLoading, error } = useRaceRegistrations(raceId);

  if (raceLoading || isLoading) {
    return (
      <div className="mx-auto max-w-5xl px-4 py-10 sm:px-6">
        <TableSkeleton rows={6} columns={4} />
      </div>
    );
  }

  if (race && user && race.organiser_id !== user.id) {
    return <Navigate to="/organiser" replace />;
  }

  if (error) {
    const message =
      isApiError(error) && error.status === 403
        ? error.message
        : isServiceUnavailable(error)
          ? "Unable to load registrations right now."
          : getMutationErrorMessage(error);

    return (
      <div className="mx-auto max-w-5xl px-4 py-10 sm:px-6">
        <EmptyState title="Unable to load registrations" description={message} />
      </div>
    );
  }

  const registrationCount = registrations?.length ?? 0;

  return (
    <div className="mx-auto max-w-5xl px-4 py-10 sm:px-6">
      <Link to="/organiser" className="text-sm font-bold text-brand hover:underline">
        ← Organiser Dashboard
      </Link>
      <h1 className="mt-4 font-display text-4xl font-black">
        {race?.name ?? `Race #${raceId}`} — Registrations
      </h1>
      {race ? (
        <>
          <p className="mt-2 text-slate-600">
            {formatRaceDate(race.date_time)} · {race.location}
          </p>
          <p className="mt-2 text-sm font-semibold text-slate-700">
            {registrationCount} / {race.max_participants} registered
          </p>
        </>
      ) : null}

      {!registrations?.length ? (
        <div className="mt-8">
          <EmptyState
            title="No one has registered for this race yet."
            description="Share your race link so participants can sign up."
          />
        </div>
      ) : (
        <div className="mt-8 overflow-x-auto rounded-2xl border-2 border-slate-200 bg-white">
          <table className="min-w-full text-left text-sm">
            <thead className="bg-slate-100 text-xs font-bold uppercase text-slate-600">
              <tr>
                <th className="px-4 py-3">Participant</th>
                <th className="px-4 py-3">Bib</th>
                <th className="px-4 py-3">Registered</th>
                <th className="px-4 py-3">Payment status</th>
              </tr>
            </thead>
            <tbody>
              {registrations.map((registration) => (
                <tr key={registration.id} className="border-t border-slate-200">
                  <td className="px-4 py-4 font-semibold">
                    {participantLabel(registration.participant_id)}
                  </td>
                  <td className="px-4 py-4">{registration.bib_number ?? "Pending"}</td>
                  <td className="px-4 py-4">{formatRaceDate(registration.registration_date)}</td>
                  <td className="px-4 py-4">
                    <Badge
                      label={registration.payment_status}
                      tone={
                        registration.payment_status === "completed"
                          ? "succeeded"
                          : registration.payment_status
                      }
                    />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
