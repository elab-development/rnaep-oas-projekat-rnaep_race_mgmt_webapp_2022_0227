import pytest
from fastapi import HTTPException

from app.core.dependencies import require_organiser, require_participant


def test_require_organiser_allows_organiser():
    result = require_organiser({"role": "organiser"})
    assert result["role"] == "organiser"


def test_require_organiser_allows_admin():
    require_organiser({"role": "admin"})


def test_require_organiser_rejects_participant():
    with pytest.raises(HTTPException) as exc_info:
        require_organiser({"role": "participant"})
    assert exc_info.value.status_code == 403


def test_require_participant_allows_participant():
    result = require_participant({"role": "participant"})
    assert result["role"] == "participant"


def test_require_participant_allows_admin():
    require_participant({"role": "admin"})


def test_require_participant_rejects_organiser():
    with pytest.raises(HTTPException) as exc_info:
        require_participant({"role": "organiser"})
    assert exc_info.value.status_code == 403
