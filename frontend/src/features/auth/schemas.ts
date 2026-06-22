import { z } from "zod";
import { Gender, TshirtSize } from "@/types/auth";

export const loginSchema = z.object({
  email: z.string().email("Enter a valid email"),
  password: z.string().min(8).max(24),
});

export const participantRegisterSchema = z.object({
  email: z.string().email().max(50),
  first_name: z.string().trim().min(2).max(50),
  last_name: z.string().trim().min(2).max(50),
  password: z.string().min(8).max(24),
  date_of_birth: z.string().min(1),
  gender: z.enum([Gender.MALE, Gender.FEMALE]),
  tshirt_size: z.enum([
    TshirtSize.S,
    TshirtSize.M,
    TshirtSize.L,
    TshirtSize.XL,
    TshirtSize.XXL,
  ]),
  emergency_contact: z.string().trim().min(10).max(20),
});

export const organiserRegisterSchema = z.object({
  email: z.string().email().max(50),
  first_name: z.string().trim().min(2).max(50),
  last_name: z.string().trim().min(2).max(50),
  password: z.string().min(8).max(24),
  organization_name: z.string().trim().min(2).max(100),
  website: z.string().url().optional().or(z.literal("")),
  description: z.string().trim().min(10).max(1000),
});
