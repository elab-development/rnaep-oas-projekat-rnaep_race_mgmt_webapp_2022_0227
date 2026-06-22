import { Link } from "react-router-dom";
import { CheckCircle2, Clock3, Loader2, XCircle } from "lucide-react";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card, CardTitle } from "@/components/ui/Card";
import { Skeleton } from "@/components/ui/Skeleton";
import type { PaymentConfirmationState } from "@/features/payments/usePaymentConfirmation";
import type { Payment } from "@/types/payment";
import { cn } from "@/utils/cn";

type PaymentDetails = {
  raceName: string;
  bibNumber: string;
  amount: number;
  paymentStatus?: Payment["status"];
};

type ActionProps = {
  onRetry?: () => void;
  onCancelRegistration?: () => void;
  onRefresh?: () => void;
  retryPending?: boolean;
  cancelPending?: boolean;
  refreshPending?: boolean;
};

const stateStyles: Record<
  PaymentConfirmationState,
  { iconBg: string; heading: string; border: string }
> = {
  loading: {
    iconBg: "bg-slate-100 text-slate-500",
    heading: "text-slate-900",
    border: "border-slate-200",
  },
  success: {
    iconBg: "bg-green-100 text-green-600",
    heading: "text-green-700",
    border: "border-green-200",
  },
  failed: {
    iconBg: "bg-red-100 text-red-600",
    heading: "text-red-700",
    border: "border-red-200",
  },
  timeout: {
    iconBg: "bg-amber-100 text-amber-700",
    heading: "text-amber-700",
    border: "border-amber-200",
  },
};

const headings: Record<PaymentConfirmationState, string> = {
  loading: "Confirming your payment…",
  success: "Payment successful",
  failed: "Payment failed",
  timeout: "Still confirming",
};

const descriptions: Record<PaymentConfirmationState, string> = {
  loading: "This usually takes a few seconds. Please keep this page open.",
  success: "You're all set for race day.",
  failed: "Your checkout was cancelled or the payment did not go through.",
  timeout: "This can take a minute. Check My Registrations for the latest status.",
};

function StateIcon({ state }: { state: PaymentConfirmationState }) {
  if (state === "loading") {
    return <Loader2 className="h-10 w-10 animate-spin" aria-hidden="true" />;
  }
  if (state === "success") {
    return <CheckCircle2 className="h-10 w-10" aria-hidden="true" />;
  }
  if (state === "failed") {
    return <XCircle className="h-10 w-10" aria-hidden="true" />;
  }
  return <Clock3 className="h-10 w-10" aria-hidden="true" />;
}

export function PaymentStatePanel({
  state,
  details,
  actions,
}: {
  state: PaymentConfirmationState;
  details?: PaymentDetails;
  actions?: ActionProps;
}) {
  const styles = stateStyles[state];

  return (
    <div className="mx-auto max-w-lg px-4 py-20 sm:px-6">
      <Card className="text-center">
        {state === "loading" ? (
          <Skeleton className={cn("mx-auto h-16 w-16 rounded-full", styles.iconBg)} />
        ) : (
          <div
            className={cn(
              "mx-auto flex h-16 w-16 items-center justify-center rounded-full",
              styles.iconBg,
            )}
          >
            <StateIcon state={state} />
          </div>
        )}

        <CardTitle className={cn("mt-6", styles.heading)}>{headings[state]}</CardTitle>
        <p className="mt-3 text-slate-600">{descriptions[state]}</p>

        {details && state !== "loading" ? (
          <div
            className={cn(
              "mt-6 rounded-2xl border-2 bg-slate-50 p-6 text-left text-sm",
              styles.border,
            )}
          >
            <p>
              <span className="font-bold text-slate-500">Race</span>
              <br />
              <span className="text-base font-semibold">{details.raceName}</span>
            </p>
            {(state === "success" || details.bibNumber) && (
              <p className="mt-4">
                <span className="font-bold text-slate-500">Bib number</span>
                <br />
                <span className="text-base font-semibold">{details.bibNumber}</span>
              </p>
            )}
            <p className="mt-4">
              <span className="font-bold text-slate-500">Amount</span>
              <br />
              <span className="text-base font-semibold text-brand">${details.amount.toFixed(2)}</span>
            </p>
            {details.paymentStatus ? (
              <p className="mt-4">
                <span className="font-bold text-slate-500">Payment status</span>
                <br />
                <Badge label={details.paymentStatus} tone={details.paymentStatus} className="mt-1" />
              </p>
            ) : null}
          </div>
        ) : null}

        <div className="mt-8 flex flex-col items-center gap-3">
          {state === "success" ? (
            <Link to="/registrations">
              <Button>View My Registrations</Button>
            </Link>
          ) : null}

          {state === "timeout" ? (
            <>
              <Button onClick={actions?.onRefresh} disabled={actions?.refreshPending}>
                {actions?.refreshPending ? "Checking…" : "Refresh status"}
              </Button>
              <Link to="/registrations" className="text-sm font-bold text-brand hover:underline">
                My Registrations
              </Link>
            </>
          ) : null}

          {state === "failed" ? (
            <>
              <Button onClick={actions?.onRetry} disabled={actions?.retryPending}>
                {actions?.retryPending ? "Starting checkout…" : "Try payment again"}
              </Button>
              <Link to="/registrations">
                <Button variant="secondary">Back to My Registrations</Button>
              </Link>
              <button
                type="button"
                onClick={actions?.onCancelRegistration}
                disabled={actions?.cancelPending}
                className="text-sm font-bold text-red-600 hover:underline disabled:opacity-50"
              >
                Cancel registration instead
              </button>
            </>
          ) : null}

          {state === "loading" ? (
            <Link to="/registrations" className="text-sm font-bold text-slate-500 hover:underline">
              My Registrations
            </Link>
          ) : null}
        </div>
      </Card>
    </div>
  );
}
