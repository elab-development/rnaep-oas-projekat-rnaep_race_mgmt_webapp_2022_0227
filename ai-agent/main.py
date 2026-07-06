"""CLI entry point.

Usage:
    python main.py --race-id 3
    python main.py --race-id 3 --output-dir output/reports
"""
import argparse
import sys

from agent.briefing_agent import UnsupportedProviderError, generate_briefing
from data.race_data import RaceNotFoundError, fetch_race_snapshot
from output.formatter import save_briefing
from weather.weather_client import WeatherUnavailableError, get_forecast


def _weather_summary_text(location: str, date_str: str) -> str:
    try:
        forecast = get_forecast(location, date_str)
        return (
            f"{forecast['weather_description']}, "
            f"{forecast['temperature_min_c']}-{forecast['temperature_max_c']}C, "
            f"{forecast['precipitation_probability_percent']}% chance of precipitation"
        )
    except WeatherUnavailableError as e:
        return f"Not available ({e})"


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate an AI race-day briefing for an ObstaRace race.")
    parser.add_argument("--race-id", type=int, required=True, help="ID of the race to generate a briefing for")
    parser.add_argument("--output-dir", default="output/reports", help="Where to save the generated Markdown report")
    args = parser.parse_args()

    try:
        race = fetch_race_snapshot(args.race_id)
    except RaceNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: could not reach the race database ({e})", file=sys.stderr)
        return 1

    date_str = race.date_time.split("T")[0].split(" ")[0]
    weather_summary = _weather_summary_text(race.location, date_str)

    race_data = {
        "name": race.name,
        "location": race.location,
        "date_time": race.date_time,
        "status": race.status,
        "max_participants": race.max_participants,
        "completed_registrations": race.completed_registrations,
        "pending_registrations": race.pending_registrations,
        "failed_registrations": race.failed_registrations,
        "capacity_utilization_percent": race.capacity_utilization_percent,
    }

    try:
        briefing = generate_briefing(race_data, weather_summary)
    except UnsupportedProviderError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: LLM call failed ({e})", file=sys.stderr)
        return 1

    print(briefing)
    saved_path = save_briefing(args.race_id, race.name, briefing, args.output_dir)
    print(f"\nSaved to: {saved_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
