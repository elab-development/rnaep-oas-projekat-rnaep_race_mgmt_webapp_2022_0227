"""CLI entry point.

Usage:
    python main.py
    python main.py --output-dir output/reports

The user is prompted interactively for the race name; the agent looks it up
among existing races and re-prompts if no match is found.
"""
import argparse
import sys

# Windows' cmd.exe/PowerShell default console codepage (cp1252/cp852) can't encode
# non-ASCII characters (e.g. accented race/location names), causing a crash on
# print; force UTF-8 on stdout/stderr so printing never crashes regardless of
# the console's codepage.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from agent.briefing_agent import UnsupportedProviderError, generate_briefing
from data.race_data import RaceNotFoundError, RaceSnapshot, fetch_race_snapshot_by_name
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


def _prompt_for_race() -> RaceSnapshot:
    """Repeatedly asks the user for a race name until an existing race is found."""
    while True:
        name = input("Unesite naziv trke: ").strip()
        if not name:
            print("Naziv trke ne sme biti prazan. Pokušajte ponovo.\n")
            continue
        try:
            return fetch_race_snapshot_by_name(name)
        except RaceNotFoundError:
            print(f"Trka '{name}' nije pronađena. Pokušajte ponovo.\n")
        except Exception as e:
            print(f"Error: could not reach the race database ({e})", file=sys.stderr)
            sys.exit(1)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate an AI race-day briefing for an ObstaRace race.")
    parser.add_argument("--output-dir", default="output/reports", help="Where to save the generated Markdown report")
    args = parser.parse_args()

    race = _prompt_for_race()

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
    saved_path = save_briefing(race.race_id, race.name, briefing, args.output_dir)
    print(f"\nSaved to: {saved_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
