export const PaymentRecordStatus = {
  PENDING: "pending",
  SUCCEEDED: "succeeded",
  FAILED: "failed",
  REFUNDED: "refunded",
} as const;

export type PaymentRecordStatus =
  (typeof PaymentRecordStatus)[keyof typeof PaymentRecordStatus];

export interface Payment {
  id: number;
  user_id: number;
  registration_id: number;
  stripe_session_id: string;
  status: PaymentRecordStatus;
  amount: number;
  checkout_url: string | null;
  created_at: string;
}

export interface PaymentCreate {
  registration_id: number;
  amount: number;
}

export interface CheckoutResponse {
  checkout_url: string;
}
