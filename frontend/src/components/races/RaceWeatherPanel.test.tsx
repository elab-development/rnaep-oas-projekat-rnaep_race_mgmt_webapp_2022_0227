import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import type { WeatherForecast } from "@/types/race";

const useRaceWeatherMock = vi.fn();

vi.mock("@/features/races/hooks", () => ({
  useRaceWeather: (raceId: number) => useRaceWeatherMock(raceId),
}));

import { RaceWeatherPanel } from "./RaceWeatherPanel";

function mockWeather(data: Partial<WeatherForecast> | undefined, isLoading = false) {
  useRaceWeatherMock.mockReturnValue({ data, isLoading });
}

describe("RaceWeatherPanel", () => {
  it("shows a skeleton while loading", () => {
    mockWeather(undefined, true);
    const { container } = render(<RaceWeatherPanel raceId={1} />);
    expect(container.querySelector(".animate-pulse")).toBeInTheDocument();
  });

  it("shows the unavailability reason when the forecast isn't available", () => {
    mockWeather({ available: false, reason: "Weather forecast is only available within 16 days." });
    render(<RaceWeatherPanel raceId={1} />);
    expect(screen.getByText(/only available within 16 days/)).toBeInTheDocument();
  });

  it("renders the forecast when available", () => {
    mockWeather({
      available: true,
      date: "2026-01-01",
      location: "Belgrade",
      temperature_min_c: 10,
      temperature_max_c: 20,
      precipitation_probability_percent: 15,
      weather_description: "Mostly clear",
    });
    render(<RaceWeatherPanel raceId={1} />);
    expect(screen.getByText(/Belgrade/)).toBeInTheDocument();
    expect(screen.getByText(/Mostly clear/)).toBeInTheDocument();
    expect(screen.getByText(/15% chance of rain/)).toBeInTheDocument();
  });
});
