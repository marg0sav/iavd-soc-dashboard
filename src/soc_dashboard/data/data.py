from functools import cache
from pathlib import Path

from soc_dashboard.repository import IncidentRepository
from soc_dashboard.service import IncidentService

# TODO: путь вычисляется от расположения этого файла и работает только при
# редактируемой установке (poetry install). При обычной установке пакета (wheel,
# например в Docker) папки data/ рядом не будет — нужен путь из настройки
# SOC_DATA_PATH (см. REFACTORING_PLAN.md, «Известные проблемы»).
PATH_TO_DATA = (
    Path(__file__).resolve().parents[3] / "data" / "new_incidents_soc_1000.parquet"
)


@cache
def get_incident_service() -> IncidentService:
    """Сервис инцидентов, общий для всех сессий: данные читаются один раз."""
    return IncidentService(IncidentRepository(PATH_TO_DATA))