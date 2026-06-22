export const RegistrationPaymentStatus = {
  PENDING: "pending",
  COMPLETED: "completed",
  FAILED: "failed",
} as const;

export type RegistrationPaymentStatus =
  (typeof RegistrationPaymentStatus)[keyof typeof RegistrationPaymentStatus];

export interface Registration {
  id: number;
  race_id: number;
  participant_id: number;
  registration_date: string;
  payment_status: RegistrationPaymentStatus;
  bib_number: string | null;
}

export interface RegistrationCreate {
  race_id: number;
}
