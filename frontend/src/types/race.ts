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

export interface WeatherForecast {
  available: boolean;
  reason?: string | null;
  date?: string | null;
  location?: string | null;
  temperature_max_c?: number | null;
  temperature_min_c?: number | null;
  precipitation_probability_percent?: number | null;
  weather_description?: string | null;
}
