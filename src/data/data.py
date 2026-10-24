from functools import cache
from pathlib import Path

from src.repository import IncidentRepository
from src.service import IncidentService

PATH_TO_DATA = (
    Path(__file__).resolve().parents[2] / "data" / "iavd_1000_incidents_raw_target.parquet"
)


@cache
def get_incident_service() -> IncidentService:
    """Сервис инцидентов, общий для всех сессий: данные читаются один раз."""
    return IncidentService(IncidentRepository(PATH_TO_DATA))
