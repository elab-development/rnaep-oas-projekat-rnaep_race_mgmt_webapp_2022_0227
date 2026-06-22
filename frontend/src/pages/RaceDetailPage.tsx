import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import toast from "react-hot-toast";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card, CardDescription, CardTitle } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { Skeleton } from "@/components/ui/Skeleton";
import { useCreateCheckout } from "@/features/payments/hooks";
import { registrationCreateSchema } from "@/features/registrations/schemas";
import { useCreateRegistration, useMyRegistrations } from "@/features/registrations/hooks";
import { useRace } from "@/features/races/hooks";
import { useAuth } from "@/hooks/useAuth";
import { RaceStatus } from "@/types/race";
import { RegistrationPaymentStatus } from "@/types/registration";
import { formatRaceDate, parseBackendDate } from "@/utils/dates";
import { getBackendFieldErrors } from "@/utils/formErrors";
import { getErrorMessage, getMutationErrorMessage } from "@/utils/errors";

export function RaceDetailPage() {
  const { id } = useParams();
  const raceId = Number(id);
  const navigate = useNavigate();
  const { isOrganiser } = useAuth();
  const { data: race, isLoading, error, refetch, isFetching } = useRace(raceId);
  const { data: registrations } = useMyRegistrations();
  const createRegistration = useCreateRegistration();
  const createCheckout = useCreateCheckout();
  const [registrationErrors, setRegistrationErrors] = useState<Record<string, string>>({});

  const existingRegistration = useMemo(
    () => registrations?.find((item) => item.race_id === raceId),
    [registrations, raceId],
  );

  const deadline = race ? parseBackendDate(race.deadline) : null;
  const isClosed =
    !race ||
    race.status !== RaceStatus.UPCOMING ||
    (deadline ? deadline.getTime() < Date.now() : false);

  let disabledReason = "";
  if (isOrganiser) disabledReason = "Switch to a participant account to register";
  else if (existingRegistration) disabledReason = "Already registered for this race";
  else if (isClosed) disabledReason = "Registration is closed";

  async function handleRegister() {
    if (!race || isOrganiser) return;

    setRegistrationErrors({});
    const parsed = registrationCreateSchema.safeParse({ race_id: race.id });
    if (!parsed.success) {
      const fieldErrors: Record<string, string> = {};
      for (const issue of parsed.error.issues) {
        const field = issue.path[0];
        if (typeof field === "string") {
          fieldErrors[field] = issue.message;
        }
      }
      setRegistrationErrors(fieldErrors);
      return;
    }

    try {
      const registration = (await createRegistration.mutateAsync({ race_id: race.id })).data;
      const checkout = (
        await createCheckout.mutateAsync({
          registration_id: registration.id,
          amount: race.price,
        })
      ).data;
      window.location.assign(checkout.checkout_url);
    } catch (caught) {
      const fieldErrors = getBackendFieldErrors(caught);
      if (fieldErrors) {
        setRegistrationErrors(fieldErrors);
        return;
      }
      toast.error(getMutationErrorMessage(caught));
    }
  }

  async function handlePayNow() {
    if (!race || !existingRegistration) return;
    try {
      const checkout = (
        await createCheckout.mutateAsync({
          registration_id: existingRegistration.id,
          amount: race.price,
        })
      ).data;
      window.location.assign(checkout.checkout_url);
    } catch (caught) {
      toast.error(getMutationErrorMessage(caught));
    }
  }

  useEffect(() => {
    if (error) {
      toast.error(getErrorMessage(error, "Failed to load race."));
    }
  }, [error]);

  if (isLoading) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-16">
        <Skeleton className="h-6 w-32" />
        <Skeleton className="mt-4 h-64 w-full" />
      </div>
    );
  }

  if (error || !race) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-16">
        <Link to="/races" className="text-sm font-bold text-brand hover:underline">
          ← Browse races
        </Link>
        <div className="mt-6">
          <EmptyState
            title={error ? "Couldn't load this race" : "Race not found"}
            description={
              error
                ? getErrorMessage(error, "Failed to load race from the server.")
                : "This race may have been removed or the link is invalid."
            }
            action={
              error ? (
                <Button onClick={() => void refetch()} disabled={isFetching}>
                  {isFetching ? "Retrying…" : "Retry"}
                </Button>
              ) : (
                <Link to="/races">
                  <Button variant="secondary">Browse Races</Button>
                </Link>
              )
            }
          />
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-3xl px-4 py-10 sm:px-6">
      <Link to="/races" className="text-sm font-bold text-brand hover:underline">
        ← Browse races
      </Link>
      <Card className="mt-4">
        <div className="flex items-start justify-between gap-3">
          <CardTitle>{race.name}</CardTitle>
          <Badge label={race.status} tone={race.status} />
        </div>
        <CardDescription>{race.location}</CardDescription>

        <dl className="mt-6 grid gap-4 sm:grid-cols-2">
          <div>
            <dt className="text-xs font-bold uppercase text-slate-500">Race date</dt>
            <dd className="font-semibold">{formatRaceDate(race.date_time)}</dd>
          </div>
          <div>
            <dt className="text-xs font-bold uppercase text-slate-500">Deadline</dt>
            <dd className="font-semibold">{formatRaceDate(race.deadline)}</dd>
          </div>
          <div>
            <dt className="text-xs font-bold uppercase text-slate-500">Capacity</dt>
            <dd className="font-semibold">{race.max_participants} spots</dd>
          </div>
          <div>
            <dt className="text-xs font-bold uppercase text-slate-500">Price</dt>
            <dd className="font-semibold text-brand">${race.price.toFixed(2)}</dd>
          </div>
        </dl>

        <div className="mt-8 border-t-2 border-slate-100 pt-6">
          {isOrganiser ? (
            <p className="text-sm text-slate-600">
              Organiser accounts cannot register for races. Switch to a participant account to
              compete.
            </p>
          ) : existingRegistration ? (
            <div className="space-y-3">
              <p className="text-sm text-slate-600">
                Registration payment status:{" "}
                <Badge
                  label={existingRegistration.payment_status}
                  tone={
                    existingRegistration.payment_status === "completed"
                      ? "succeeded"
                      : existingRegistration.payment_status
                  }
                />
              </p>
              {existingRegistration.payment_status !== RegistrationPaymentStatus.COMPLETED ? (
                <Button onClick={handlePayNow} disabled={createCheckout.isPending}>
                  {existingRegistration.payment_status === RegistrationPaymentStatus.FAILED
                    ? "Retry payment"
                    : "Complete payment"}
                </Button>
              ) : null}
              <Button variant="secondary" onClick={() => navigate("/registrations")}>
                View my registrations
              </Button>
            </div>
          ) : (
            <>
              <Button
                disabled={Boolean(disabledReason) || createRegistration.isPending}
                onClick={handleRegister}
              >
                {createRegistration.isPending ? "Registering..." : "Register & Pay"}
              </Button>
              {Object.entries(registrationErrors).map(([field, message]) => (
                <p key={field} className="mt-2 text-sm text-red-600">
                  {message}
                </p>
              ))}
              {disabledReason ? (
                <p className="mt-2 text-sm font-medium text-amber-700">{disabledReason}</p>
              ) : null}
            </>
          )}
        </div>
      </Card>
    </div>
  );
}
