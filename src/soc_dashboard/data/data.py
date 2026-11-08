from functools import cache
from pathlib import Path

from soc_dashboard.repository import IncidentRepository
from soc_dashboard.service import IncidentService

PATH_TO_DATA = (
    Path(__file__).resolve().parents[3] / "data" / "new_incidents_soc_1000.parquet"
)


@cache
def get_incident_service() -> IncidentService:
    """Сервис инцидентов, общий для всех сессий: данные читаются один раз."""
    return IncidentService(IncidentRepository(PATH_TO_DATA))

@cache
def get_ml_model_metadata() -> dict | None:
    pass