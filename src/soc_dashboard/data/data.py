import json
from functools import cache
from pathlib import Path

import pandas as pd

from soc_dashboard.domain.ml_model_metadata import MLModelMetadata
from soc_dashboard.inference.evaluation import build_prediction_table
from soc_dashboard.model.catboost_model import SocCatBoostModel
from soc_dashboard.repository import IncidentRepository
from soc_dashboard.service import IncidentService

PATH_TO_DATA = (
    Path(__file__).resolve().parents[3] / "data" / "new_incidents_soc_1000.parquet"
)

PATH_TO_ML_MODEL_METADATA = (
    Path(__file__).resolve().parents[3] / "ml_models" / "verdict" / "metadata.json"
)

PATH_TO_ML_MODEL_JOBLIB = (
    Path(__file__).resolve().parents[3] / "ml_models" / "verdict" / "model.joblib"
)

PATH_TO_PURE_TEST_DATA = (
    Path(__file__).resolve().parents[3] / "data" / "pure_test.parquet"
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

    try:
        with open(PATH_TO_ML_MODEL_METADATA, encoding="utf-8") as json_file:
            return MLModelMetadata.from_dict(json.load(json_file))
    except Exception:  # noqa: BLE001
        # NOTE: Сейчас считаем что нам норм с noqa BLE001.
        # TODO: logger?
        return None


@cache
def get_pure_test_predictions() -> pd.DataFrame | None:
    """Прогнозы модели на pure_test, None - если нет модели или выборки."""
    if not (PATH_TO_ML_MODEL_JOBLIB).is_file() or not (PATH_TO_ML_MODEL_JOBLIB).exists():
        return None

    if not PATH_TO_PURE_TEST_DATA.is_file():
        return None

    model = SocCatBoostModel(PATH_TO_ML_MODEL_JOBLIB)
    incidents = pd.read_parquet(PATH_TO_PURE_TEST_DATA)

    return build_prediction_table(
        incidents,
        model.predict_positive_probabilities(incidents),
        model.threshold,
    )
