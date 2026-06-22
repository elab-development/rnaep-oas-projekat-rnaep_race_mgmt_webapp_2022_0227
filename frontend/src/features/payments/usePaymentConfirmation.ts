import { useCallback, useEffect, useState } from "react";
import { paymentApi } from "@/api/paymentApi";
import type { Payment } from "@/types/payment";
import { PaymentRecordStatus } from "@/types/payment";

const POLL_INTERVAL_MS = 2_000;
const POLL_TIMEOUT_MS = 25_000;
const REQUEST_TIMEOUT_MS = 8_000;

export type PaymentConfirmationState = "loading" | "success" | "failed" | "timeout";

export type PaymentQueryParams = {
  paymentId?: number;
  registrationId?: number;
  sessionId?: string | null;
};

function isTerminalStatus(status: Payment["status"] | undefined): boolean {
  return (
    status === PaymentRecordStatus.SUCCEEDED ||
    status === PaymentRecordStatus.FAILED ||
    status === PaymentRecordStatus.REFUNDED
  );
}

export async function resolvePayment(params: PaymentQueryParams): Promise<Payment | null> {
  if (!params.paymentId || params.paymentId <= 0) return null;

  const lookup = async () => {
    try {
      return (await paymentApi.getById(params.paymentId!)).data;
    } catch {
      return null;
    }
  };

  return Promise.race([
    lookup(),
    new Promise<null>((resolve) => {
      window.setTimeout(() => resolve(null), REQUEST_TIMEOUT_MS);
    }),
  ]);
}

type Options = PaymentQueryParams & {
  enabled?: boolean;
  /** Skip polling — show failed UI immediately (cancel URL landing). */
  assumeFailed?: boolean;
};

export function usePaymentConfirmation(options: Options) {
  const enabled = options.enabled ?? true;
  const [payment, setPayment] = useState<Payment | null>(null);
  const [state, setState] = useState<PaymentConfirmationState>(
    options.assumeFailed ? "failed" : "loading",
  );
  const [refreshCount, setRefreshCount] = useState(0);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const refresh = useCallback(() => {
    setRefreshCount((count) => count + 1);
    setIsRefreshing(true);
    setState("loading");
  }, []);

  useEffect(() => {
    if (!enabled) return;

    const queryParams: PaymentQueryParams = {
      paymentId: options.paymentId,
      registrationId: options.registrationId,
      sessionId: options.sessionId,
    };

    if (options.assumeFailed && refreshCount === 0) {
      let cancelled = false;
      void resolvePayment(queryParams).then((resolved) => {
        if (cancelled) return;
        setPayment(resolved);
        if (resolved?.status === PaymentRecordStatus.SUCCEEDED) {
          setState("success");
        } else {
          setState("failed");
        }
      });
      return () => {
        cancelled = true;
      };
    }

    let cancelled = false;
    const startedAt = Date.now();

    function stopPolling(next: PaymentConfirmationState, intervalId: ReturnType<typeof setInterval>) {
      if (cancelled) return;
      setState(next);
      setIsRefreshing(false);
      clearInterval(intervalId);
    }

    async function poll(intervalId: ReturnType<typeof setInterval>) {
      if (cancelled) return;

      const resolved = await resolvePayment(queryParams);
      if (cancelled) return;

      setPayment(resolved);

      if (resolved?.status === PaymentRecordStatus.SUCCEEDED) {
        stopPolling("success", intervalId);
        return;
      }
      if (isTerminalStatus(resolved?.status)) {
        stopPolling("failed", intervalId);
        return;
      }

      if (Date.now() - startedAt >= POLL_TIMEOUT_MS) {
        stopPolling("timeout", intervalId);
      }
    }

    const intervalId = window.setInterval(() => {
      void poll(intervalId);
    }, POLL_INTERVAL_MS);
    void poll(intervalId);

    const hardStopId = window.setTimeout(() => {
      if (cancelled) return;
      setState((current) => {
        if (current === "loading") {
          setIsRefreshing(false);
          clearInterval(intervalId);
          return "timeout";
        }
        return current;
      });
    }, POLL_TIMEOUT_MS + 250);

    return () => {
      cancelled = true;
      clearInterval(intervalId);
      clearTimeout(hardStopId);
    };
  }, [
    enabled,
    options.assumeFailed,
    options.paymentId,
    options.registrationId,
    options.sessionId,
    refreshCount,
  ]);

  return { payment, state, refresh, isRefreshing };
}
