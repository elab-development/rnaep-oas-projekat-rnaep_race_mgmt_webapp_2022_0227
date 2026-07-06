"""Formats the final briefing into a saved Markdown file with a consistent header/footer."""
from datetime import datetime, timezone
from pathlib import Path


def save_briefing(race_id: int, race_name: str, briefing_markdown: str, output_dir: str = "output/reports") -> Path:
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    safe_name = "".join(c if c.isalnum() else "-" for c in race_name).strip("-")
    file_path = Path(output_dir) / f"race-{race_id}-{safe_name}-{timestamp}.md"

    header = f"# Race Day Briefing — {race_name} (Race #{race_id})\n\n"
    footer = f"\n\n---\n*Generated {timestamp} UTC by the ObstaRace Race Briefing Agent.*\n"

    file_path.write_text(header + briefing_markdown + footer, encoding="utf-8")
    return file_path
