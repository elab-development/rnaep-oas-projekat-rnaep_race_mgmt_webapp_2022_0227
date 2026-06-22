import { apiClient } from "./client";
import type { CheckoutResponse, Payment, PaymentCreate } from "@/types/payment";

export const paymentApi = {
  createCheckout(payload: PaymentCreate) {
    return apiClient.post<CheckoutResponse>("/payments/checkout", payload);
  },

  getById(paymentId: number) {
    return apiClient.get<Payment>(`/payments/${paymentId}`);
  },
};
