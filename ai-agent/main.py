"""CLI entry point.

Usage:
    python main.py
    python main.py --output-dir output/reports

The user is prompted interactively for the race name; the agent looks it up
among existing races and re-prompts if no match is found.
"""
import argparse
import os
import sys

# Windows' cmd.exe/PowerShell default console codepage (cp1252/cp852) can't encode
# non-ASCII characters (e.g. accented race/location names), causing a crash on
# print; force UTF-8 on stdout/stderr so printing never crashes regardless of
# the console's codepage.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from agent.briefing_agent import UnsupportedProviderError, generate_briefing
from data.race_data import RaceNotFoundError, RaceSnapshot, fetch_race_snapshot_by_name, list_race_names
from output.formatter import save_briefing
from weather.weather_client import WeatherUnavailableError, get_forecast


class _Style:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    CYAN = "\033[36m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    RED = "\033[31m"


def _enable_console_colors() -> None:
    """Turns on ANSI escape processing in classic Windows consoles (cmd.exe,
    Windows PowerShell); a no-op everywhere else, including VS Code's terminal."""
    if os.name == "nt":
        os.system("")


def _banner() -> None:
    line = "=" * 50
    print(f"{_Style.BOLD}{_Style.CYAN}{line}")
    print("  ObstaRace — Race Day Briefing Agent")
    print(f"{line}{_Style.RESET}")
    print("Zdravo! Ja sam Race Day Briefing Agent, AI asistent za ObstaRace.")
    print("Pomažem organizatorima trka tako što na osnovu podataka o trci i")
    print("vremenskoj prognozi generišem kratak izveštaj pred sam dan trke.\n", flush=True)


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
        name = input(f"{_Style.YELLOW}> Unesite naziv trke: {_Style.RESET}").strip()
        if not name:
            print(f"{_Style.RED}Naziv trke ne sme biti prazan. Pokušajte ponovo.{_Style.RESET}\n")
            continue
        try:
            return fetch_race_snapshot_by_name(name)
        except RaceNotFoundError:
            print(f"{_Style.RED}Trka '{name}' nije pronađena.{_Style.RESET}")
            existing = list_race_names()
            if existing:
                print(f"{_Style.DIM}Postojeće trke:{_Style.RESET}")
                for existing_name in existing:
                    print(f"  {_Style.DIM}•{_Style.RESET} {existing_name}")
            print("Pokušajte ponovo.\n")
        except Exception as e:
            print(f"{_Style.RED}Error: could not reach the race database ({e}){_Style.RESET}", file=sys.stderr)
            sys.exit(1)


def main() -> int:
    _enable_console_colors()
    parser = argparse.ArgumentParser(description="Generate an AI race-day briefing for an ObstaRace race.")
    parser.add_argument("--output-dir", default="output/reports", help="Where to save the generated Markdown report")
    args = parser.parse_args()

    _banner()
    race = _prompt_for_race()
    print(f"{_Style.GREEN}✓ Pronađena trka: {race.name} (#{race.race_id}) — {race.location}{_Style.RESET}\n", flush=True)

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

    print(f"{_Style.DIM}Generišem AI izveštaj...{_Style.RESET}", flush=True)

    try:
        briefing = generate_briefing(race_data, weather_summary)
    except UnsupportedProviderError as e:
        print(f"{_Style.RED}Error: {e}{_Style.RESET}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"{_Style.RED}Error: LLM call failed ({e}){_Style.RESET}", file=sys.stderr)
        return 1

    divider = f"{_Style.BOLD}{_Style.CYAN}{'-' * 50}{_Style.RESET}"
    print(divider)
    print(briefing)
    print(divider, flush=True)

    saved_path = save_briefing(race.race_id, race.name, briefing, args.output_dir)
    print(f"{_Style.GREEN}✓ Sačuvano u: {saved_path}{_Style.RESET}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
