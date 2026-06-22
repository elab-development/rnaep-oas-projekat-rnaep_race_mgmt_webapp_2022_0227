import { z } from "zod";

export const registrationCreateSchema = z.object({
  race_id: z.number().int().positive(),
  bib_number: z
    .string()
    .optional()
    .superRefine((value, ctx) => {
      if (value !== undefined && !value.trim()) {
        ctx.addIssue({
          code: "custom",
          message: "Bib number cannot be empty",
        });
      }
    }),
});

export type RegistrationCreateFormValues = z.infer<typeof registrationCreateSchema>;
