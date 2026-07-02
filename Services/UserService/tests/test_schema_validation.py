from datetime import UTC, date, datetime, timedelta

import pytest
from pydantic import ValidationError

from app.api.schema import OrganiserCreate, ParticipantCreate
from app.enum import GenderEnum


def make_participant(**overrides):
    data = dict(
        email="runner@example.com",
        first_name="Ana",
        last_name="Anic",
        password="password123",
        date_of_birth=date(1995, 1, 1),
        gender=GenderEnum.FEMALE,
        tshirt_size=None,
        emergency_contact="+381601234567",
    )
    data.update(overrides)
    return data


def make_organiser(**overrides):
    data = dict(
        email="org@example.com",
        first_name="Org",
        last_name="Team",
        password="password123",
        organization_name="Trail Runners",
        website=None,
        description="A community trail running club active since 2010.",
    )
    data.update(overrides)
    return data


def test_valid_participant_passes():
    ParticipantCreate(**make_participant())


def _utc_today() -> date:
    # Matches the validator's own reference point (datetime.now(UTC).date()).
    return datetime.now(UTC).date()


def test_participant_under_18_is_rejected():
    today = _utc_today()
    seventeen_years_ago = today.replace(year=today.year - 17)
    with pytest.raises(ValidationError):
        ParticipantCreate(**make_participant(date_of_birth=seventeen_years_ago))


def test_participant_exactly_18_is_accepted():
    today = _utc_today()
    eighteen_years_ago = today.replace(year=today.year - 18)
    ParticipantCreate(**make_participant(date_of_birth=eighteen_years_ago))


def test_participant_future_date_of_birth_is_rejected():
    with pytest.raises(ValidationError):
        ParticipantCreate(**make_participant(date_of_birth=_utc_today() + timedelta(days=1)))


def test_participant_password_too_short_is_rejected():
    with pytest.raises(ValidationError):
        ParticipantCreate(**make_participant(password="short1"))


def test_participant_password_too_long_is_rejected():
    with pytest.raises(ValidationError):
        ParticipantCreate(**make_participant(password="a" * 25))


def test_participant_emergency_contact_too_short_is_rejected():
    with pytest.raises(ValidationError):
        ParticipantCreate(**make_participant(emergency_contact="123"))


def test_participant_name_too_short_is_rejected():
    with pytest.raises(ValidationError):
        ParticipantCreate(**make_participant(first_name="A"))


def test_valid_organiser_passes():
    OrganiserCreate(**make_organiser())


def test_organiser_website_without_scheme_is_rejected():
    with pytest.raises(ValidationError):
        OrganiserCreate(**make_organiser(website="example.com"))


def test_organiser_blank_website_becomes_none():
    organiser = OrganiserCreate(**make_organiser(website="   "))
    assert organiser.website is None


def test_organiser_description_too_short_is_rejected():
    with pytest.raises(ValidationError):
        OrganiserCreate(**make_organiser(description="too short"))
