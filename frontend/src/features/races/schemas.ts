import { z } from "zod";
import { RaceStatus } from "@/types/race";

const raceFieldSchema = z.object({
  name: z.string().superRefine((value, ctx) => {
    if (!value.trim()) {
      ctx.addIssue({
        code: "custom",
        message: "Name cannot be empty",
      });
    }
  }),
  date_time: z.string().min(1, "Race date is required"),
  deadline: z.string().min(1, "Deadline is required"),
  location: z.string().trim().min(1, "Location is required"),
  max_participants: z.coerce
    .number()
    .refine((value) => value > 0, {
      message: "Number of participants must be greater than 0",
    }),
  price: z.coerce.number().refine((value) => value >= 0, {
    message: "Price must be a positive number",
  }),
  status: z.enum([
    RaceStatus.UPCOMING,
    RaceStatus.COMPLETED,
    RaceStatus.CANCELLED,
  ]),
});

export const raceCreateSchema = raceFieldSchema
  .refine((data) => new Date(data.deadline) < new Date(data.date_time), {
    message: "Deadline must be before the race date",
    path: ["deadline"],
  })
  .refine((data) => new Date(data.date_time) > new Date(), {
    message: "Race date must be in the future",
    path: ["date_time"],
  });

export const raceEditSchema = raceFieldSchema.refine(
  (data) => new Date(data.deadline) < new Date(data.date_time),
  {
    message: "Deadline must be before the race date",
    path: ["deadline"],
  },
);

export type RaceCreateFormInput = z.input<typeof raceCreateSchema>;
export type RaceCreateFormValues = z.output<typeof raceCreateSchema>;
export type RaceEditFormInput = z.input<typeof raceEditSchema>;
export type RaceEditFormValues = z.output<typeof raceEditSchema>;
