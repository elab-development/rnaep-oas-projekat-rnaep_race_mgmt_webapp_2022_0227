import { useQueries } from "@tanstack/react-query";
import toast from "react-hot-toast";
import { Link } from "react-router-dom";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { EmptyState } from "@/components/ui/EmptyState";
import { Modal } from "@/components/ui/Modal";
import { TableSkeleton } from "@/components/ui/Skeleton";
import { useCreateCheckout } from "@/features/payments/hooks";
import { useCancelRegistration, useMyRegistrations } from "@/features/registrations/hooks";
import { raceApi } from "@/api/raceApi";
import { RegistrationPaymentStatus } from "@/types/registration";
import { formatRaceDate } from "@/utils/dates";
import { getMutationErrorMessage } from "@/utils/errors";
import { useState } from "react";

export function MyRegistrationsPage() {
  const { data: registrations, isLoading } = useMyRegistrations();
  const cancelRegistration = useCancelRegistration();
  const createCheckout = useCreateCheckout();
  const [pendingCancelId, setPendingCancelId] = useState<number | null>(null);
  const [payingId, setPayingId] = useState<number | null>(null);

  const raceQueries = useQueries({
    queries: (registrations ?? []).map((registration) => ({
      queryKey: ["race", registration.race_id],
      queryFn: async () => (await raceApi.getById(registration.race_id)).data,
    })),
  });

  async function confirmCancel() {
    if (!pendingCancelId) return;
    try {
      await cancelRegistration.mutateAsync(pendingCancelId);
      toast.success("Registration cancelled");
      setPendingCancelId(null);
    } catch (error) {
      toast.error(getMutationErrorMessage(error));
    }
  }

  async function handlePayment(registrationId: number, raceIndex: number) {
    const race = raceQueries[raceIndex]?.data;
    if (!race) {
      toast.error("Race details unavailable. Please try again.");
      return;
    }
    setPayingId(registrationId);
    try {
      const checkout = (
        await createCheckout.mutateAsync({
          registration_id: registrationId,
          amount: race.price,
        })
      ).data;
      window.location.assign(checkout.checkout_url);
    } catch (error) {
      toast.error(getMutationErrorMessage(error));
      setPayingId(null);
    }
  }

  if (isLoading) {
    return (
      <div className="mx-auto max-w-5xl px-4 py-10 sm:px-6">
        <TableSkeleton rows={5} columns={5} />
      </div>
    );
  }

  if (!registrations?.length) {
    return (
      <div className="mx-auto max-w-5xl px-4 py-16">
        <EmptyState
          title="No registrations yet"
          description="Browse upcoming races and secure your spot."
          action={
            <Link to="/races">
              <Button>Browse Races</Button>
            </Link>
          }
        />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-5xl px-4 py-10 sm:px-6">
      <h1 className="font-display text-4xl font-black">My Registrations</h1>
      <div className="mt-8 overflow-x-auto rounded-2xl border-2 border-slate-200 bg-white">
        <table className="min-w-full text-left text-sm">
          <thead className="bg-slate-100 text-xs font-bold uppercase text-slate-600">
            <tr>
              <th className="px-4 py-3">Race</th>
              <th className="px-4 py-3">Date</th>
              <th className="px-4 py-3">Bib</th>
              <th className="px-4 py-3">Payment</th>
              <th className="px-4 py-3">Actions</th>
            </tr>
          </thead>
          <tbody>
            {registrations.map((registration, index) => {
              const race = raceQueries[index]?.data;
              const needsPayment =
                registration.payment_status === RegistrationPaymentStatus.PENDING ||
                registration.payment_status === RegistrationPaymentStatus.FAILED;
              const paymentLabel =
                registration.payment_status === RegistrationPaymentStatus.FAILED
                  ? "Retry payment"
                  : "Complete payment";

              return (
                <tr key={registration.id} className="border-t border-slate-200">
                  <td className="px-4 py-4 font-semibold">
                    {race?.name ?? `Race #${registration.race_id}`}
                  </td>
                  <td className="px-4 py-4">{race ? formatRaceDate(race.date_time) : "—"}</td>
                  <td className="px-4 py-4">{registration.bib_number ?? "Pending"}</td>
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
                  <td className="px-4 py-4">
                    <div className="flex flex-wrap gap-2">
                      {needsPayment ? (
                        <Button
                          className="px-3 py-1.5 text-xs"
                          disabled={payingId === registration.id}
                          onClick={() => handlePayment(registration.id, index)}
                        >
                          {payingId === registration.id ? "Redirecting…" : paymentLabel}
                        </Button>
                      ) : null}
                      <Button
                        variant="danger"
                        className="px-3 py-1.5 text-xs"
                        onClick={() => setPendingCancelId(registration.id)}
                      >
                        Cancel
                      </Button>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <Modal
        open={pendingCancelId !== null}
        title="Cancel registration?"
        description="This action cannot be undone."
        confirmLabel="Cancel registration"
        onConfirm={confirmCancel}
        onClose={() => setPendingCancelId(null)}
      />
    </div>
  );
}
