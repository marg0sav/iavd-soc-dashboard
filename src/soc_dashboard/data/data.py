import json
from functools import cache
from pathlib import Path

from soc_dashboard.domain.ml_model_metadata import MLModelMetadata
from soc_dashboard.repository import IncidentRepository
from soc_dashboard.service import IncidentService

PATH_TO_DATA = (
    Path(__file__).resolve().parents[3] / "data" / "new_incidents_soc_1000.parquet"
)

PATH_TO_ML_MODEL_METADATA = (
    Path(__file__).resolve().parents[3] / "ml_models" / "verdict" / "metadata.json"
)


@cache
def get_incident_service() -> IncidentService:
    """Сервис инцидентов, общий для всех сессий: данные читаются один раз."""
    return IncidentService(IncidentRepository(PATH_TO_DATA))


@cache
def get_ml_model_metadata() -> MLModelMetadata | None:
    """Метаданные ML-модели из metadata.json, None - если модель не обучена."""
    if not PATH_TO_ML_MODEL_METADATA.is_file():
        return None

    if not PATH_TO_ML_MODEL_METADATA.exists():
        return None

    with open(PATH_TO_ML_MODEL_METADATA, encoding="utf-8") as json_file:
        return MLModelMetadata.from_dict(json.load(json_file))
