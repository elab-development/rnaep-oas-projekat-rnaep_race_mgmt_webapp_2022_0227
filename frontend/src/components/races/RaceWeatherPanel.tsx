import { Skeleton } from "@/components/ui/Skeleton";
import { useRaceWeather } from "@/features/races/hooks";

type Props = {
  raceId: number;
};

export function RaceWeatherPanel({ raceId }: Props) {
  const { data: weather, isLoading } = useRaceWeather(raceId);

  if (isLoading) {
    return <Skeleton className="mt-6 h-16 w-full" />;
  }

  if (!weather || !weather.available) {
    return (
      <div className="mt-6 rounded-xl border-2 border-slate-100 bg-slate-50 p-4 text-sm text-slate-500">
        {weather?.reason ?? "Weather forecast is not available for this race."}
      </div>
    );
  }

  return (
    <div className="mt-6 rounded-xl border-2 border-slate-100 bg-slate-50 p-4">
      <p className="text-xs font-bold uppercase text-slate-500">
        Forecast for {weather.location} on {weather.date}
      </p>
      <p className="mt-1 text-sm font-semibold text-slate-800">
        {weather.weather_description} · {weather.temperature_min_c}°C – {weather.temperature_max_c}°C
        {" · "}
        {weather.precipitation_probability_percent}% chance of rain
      </p>
      <p className="mt-1 text-xs text-slate-400">Data from Open-Meteo</p>
    </div>
  );
}
