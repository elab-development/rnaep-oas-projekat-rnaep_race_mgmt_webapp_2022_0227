export const RaceStatus = {
  UPCOMING: "upcoming",
  COMPLETED: "completed",
  CANCELLED: "cancelled",
} as const;

export type RaceStatus = (typeof RaceStatus)[keyof typeof RaceStatus];

export interface Race {
  id: number;
  name: string;
  date_time: string;
  deadline: string;
  location: string;
  max_participants: number;
  status: RaceStatus;
  price: number;
  organiser_id: number;
  created_at: string;
  is_active: boolean;
}

export interface RaceCreate {
  name: string;
  date_time: string;
  deadline: string;
  location: string;
  max_participants: number;
  status?: RaceStatus;
  price: number;
}

export interface RaceUpdate {
  name?: string;
  date_time?: string;
  deadline?: string;
  location?: string;
  max_participants?: number;
  status?: RaceStatus;
  price?: number;
}
