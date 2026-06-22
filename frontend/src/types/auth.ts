export const Gender = {
  MALE: "MALE",
  FEMALE: "FEMALE",
} as const;

export type Gender = (typeof Gender)[keyof typeof Gender];

export const TshirtSize = {
  S: "S",
  M: "M",
  L: "L",
  XL: "XL",
  XXL: "XXL",
} as const;

export type TshirtSize = (typeof TshirtSize)[keyof typeof TshirtSize];

export type UserRole = "participant" | "organiser" | "admin" | "user";

export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  is_active: boolean;
  created_at: string;
  participant: {
    date_of_birth: string;
    gender: Gender;
    tshirt_size: TshirtSize | null;
    emergency_contact: string;
  } | null;
  organiser: {
    organization_name: string;
    website: string | null;
    description: string;
    is_verified: boolean;
  } | null;
  admin: { admin_level: number } | null;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface ParticipantRegisterRequest {
  email: string;
  first_name: string;
  last_name: string;
  password: string;
  date_of_birth: string;
  gender: Gender;
  tshirt_size?: TshirtSize | null;
  emergency_contact: string;
}

export interface OrganiserRegisterRequest {
  email: string;
  first_name: string;
  last_name: string;
  password: string;
  organization_name: string;
  website?: string | null;
  description: string;
}

export interface MessageResponse {
  message: string;
}

export function resolveUserRole(user: User): UserRole {
  if (user.admin) return "admin";
  if (user.organiser) return "organiser";
  if (user.participant) return "participant";
  return "user";
}

export function isOrganiser(user: User | null | undefined): boolean {
  return Boolean(user?.organiser || user?.admin);
}

export function isParticipant(user: User | null | undefined): boolean {
  return Boolean(user?.participant || user?.admin);
}
