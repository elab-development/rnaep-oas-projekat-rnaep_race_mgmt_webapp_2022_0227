"""Fetches real race and registration data straight from RaceService's PostgreSQL
database - this is the "external data" this agent is built around: it reads the
same production data the ObstaRace platform itself uses, not a synthetic sample.
"""
from dataclasses import dataclass

from sqlalchemy import create_engine, text

from config import config


class RaceNotFoundError(Exception):
    pass


@dataclass
class RaceSnapshot:
    race_id: int
    name: str
    location: str
    date_time: str
    max_participants: int
    price: float
    status: str
    completed_registrations: int
    pending_registrations: int
    failed_registrations: int

    @property
    def capacity_utilization_percent(self) -> float:
        if self.max_participants == 0:
            return 0.0
        confirmed = self.completed_registrations + self.pending_registrations
        return round((confirmed / self.max_participants) * 100, 1)


def _build_snapshot(conn, race_row) -> RaceSnapshot:
    counts = (
        conn.execute(
            text(
                "SELECT payment_status, COUNT(*) AS cnt FROM registrations "
                "WHERE race_id = :race_id GROUP BY payment_status"
            ),
            {"race_id": race_row["id"]},
        )
        .mappings()
        .all()
    )
    count_by_status = {row["payment_status"]: row["cnt"] for row in counts}

    return RaceSnapshot(
        race_id=race_row["id"],
        name=race_row["name"],
        location=race_row["location"],
        date_time=str(race_row["date_time"]),
        max_participants=race_row["max_participants"],
        price=float(race_row["price"]),
        status=race_row["status"],
        completed_registrations=count_by_status.get("completed", 0),
        pending_registrations=count_by_status.get("pending", 0),
        failed_registrations=count_by_status.get("failed", 0),
    )


def fetch_race_snapshot(race_id: int) -> RaceSnapshot:
    """Fetch a race plus a breakdown of its registrations by payment status."""
    engine = create_engine(config.race_database_url)
    try:
        with engine.connect() as conn:
            race_row = (
                conn.execute(
                    text(
                        "SELECT id, name, location, date_time, max_participants, price, status "
                        "FROM races WHERE id = :race_id"
                    ),
                    {"race_id": race_id},
                )
                .mappings()
                .first()
            )

            if race_row is None:
                raise RaceNotFoundError(f"No race found with id={race_id}")

            return _build_snapshot(conn, race_row)
    finally:
        engine.dispose()


def fetch_race_snapshot_by_name(name: str) -> RaceSnapshot:
    """Fetch a race by a case-insensitive partial name match (first match by id)."""
    engine = create_engine(config.race_database_url)
    try:
        with engine.connect() as conn:
            race_row = (
                conn.execute(
                    text(
                        "SELECT id, name, location, date_time, max_participants, price, status "
                        "FROM races WHERE name ILIKE :pattern ORDER BY id LIMIT 1"
                    ),
                    {"pattern": f"%{name}%"},
                )
                .mappings()
                .first()
            )

            if race_row is None:
                raise RaceNotFoundError(f"No race found matching name '{name}'")

            return _build_snapshot(conn, race_row)
    finally:
        engine.dispose()


def list_race_names(limit: int = 15) -> list[str]:
    """Existing race names (most recent first), used as a hint when a name lookup fails."""
    engine = create_engine(config.race_database_url)
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text("SELECT name FROM races ORDER BY date_time DESC LIMIT :limit"),
                {"limit": limit},
            ).all()
            return [row[0] for row in rows]
    finally:
        engine.dispose()
