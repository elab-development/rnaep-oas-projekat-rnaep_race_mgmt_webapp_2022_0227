import { useMutation, useQueryClient } from "@tanstack/react-query";
import { paymentApi } from "@/api/paymentApi";
import { registrationKeys } from "@/features/registrations/hooks";

export { resolvePayment, usePaymentConfirmation } from "./usePaymentConfirmation";
export type {
  PaymentConfirmationState,
  PaymentQueryParams,
} from "./usePaymentConfirmation";

export function useCreateCheckout() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: paymentApi.createCheckout,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: registrationKeys.mine() });
    },
  });
}
