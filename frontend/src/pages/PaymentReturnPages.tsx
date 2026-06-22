import { useMemo } from "react";
import { useSearchParams } from "react-router-dom";
import toast from "react-hot-toast";
import { PaymentStatePanel } from "@/components/payments/PaymentStatePanel";
import { useCreateCheckout } from "@/features/payments/hooks";
import {
  usePaymentConfirmation,
  type PaymentQueryParams,
} from "@/features/payments/usePaymentConfirmation";
import { useCancelRegistration, useMyRegistrations } from "@/features/registrations/hooks";
import { useRace } from "@/features/races/hooks";
import { getMutationErrorMessage } from "@/utils/errors";

function usePaymentQueryParams(): PaymentQueryParams {
  const [searchParams] = useSearchParams();
  return useMemo(() => {
    const registrationId = Number(searchParams.get("registration_id") ?? 0);
    const paymentId = Number(searchParams.get("payment_id") ?? 0);
    return {
      registrationId: registrationId > 0 ? registrationId : undefined,
      paymentId: paymentId > 0 ? paymentId : undefined,
      sessionId: searchParams.get("session_id"),
    };
  }, [searchParams]);
}

function usePaymentContext(params: PaymentQueryParams, payment?: { registration_id: number; amount: number } | null) {
  const registrationId = params.registrationId ?? payment?.registration_id;
  const { data: registrations } = useMyRegistrations();
  const registration = registrations?.find((item) => item.id === registrationId);
  const { data: race } = useRace(registration?.race_id ?? 0);

  return {
    registrationId,
    registration,
    race,
    amount: payment?.amount ?? race?.price ?? 0,
  };
}

export function PaymentFailedPage() {
  const params = usePaymentQueryParams();
  const { payment, state, refresh, isRefreshing } = usePaymentConfirmation({
    ...params,
    assumeFailed: true,
  });
  const createCheckout = useCreateCheckout();
  const cancelRegistration = useCancelRegistration();
  const { registrationId, registration, race, amount } = usePaymentContext(params, payment);

  async function handleRetryPayment() {
    if (!registrationId || amount <= 0) {
      toast.error("Missing registration details. Open My Registrations to retry payment.");
      return;
    }
    try {
      const checkout = (
        await createCheckout.mutateAsync({
          registration_id: registrationId,
          amount,
        })
      ).data;
      window.location.assign(checkout.checkout_url);
    } catch (error) {
      toast.error(getMutationErrorMessage(error));
    }
  }

  async function handleCancelRegistration() {
    if (!registrationId) {
      toast.error("Missing registration details.");
      return;
    }
    try {
      await cancelRegistration.mutateAsync(registrationId);
      toast.success("Registration cancelled");
    } catch (error) {
      toast.error(getMutationErrorMessage(error));
    }
  }

  const details = {
    raceName: race?.name ?? (registration ? `Race #${registration.race_id}` : "Your race"),
    bibNumber: registration?.bib_number ?? "Pending",
    amount,
    paymentStatus: payment?.status,
  };

  return (
    <PaymentStatePanel
      state={state}
      details={details}
      actions={{
        onRetry: handleRetryPayment,
        onCancelRegistration: handleCancelRegistration,
        onRefresh: refresh,
        retryPending: createCheckout.isPending,
        cancelPending: cancelRegistration.isPending,
        refreshPending: isRefreshing,
      }}
    />
  );
}

/** @deprecated Use PaymentFailedPage — kept for old cancel URL paths */
export const PaymentCancelPage = PaymentFailedPage;
