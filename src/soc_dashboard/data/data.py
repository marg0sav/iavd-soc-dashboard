import json
from functools import cache
from pathlib import Path

import pandas as pd

from soc_dashboard.domain.columns import Col
from soc_dashboard.domain.ml_model_metadata import MLModelMetadata
from soc_dashboard.inference.evaluation import build_prediction_table
from soc_dashboard.model.catboost_model import SocCatBoostModel
from soc_dashboard.repository import IncidentRepository
from soc_dashboard.service import IncidentService

PATH_TO_DATA = (
    Path(__file__).resolve().parents[3] / "data" / "new_incidents_soc_1000.parquet"
)

PATH_TO_MODEL_DIRECTORY = Path(__file__).resolve().parents[3] / "ml_models" / "verdict"

PATH_TO_ML_MODEL_METADATA = PATH_TO_MODEL_DIRECTORY / "metadata.json"

PATH_TO_ML_MODEL_JOBLIB = PATH_TO_MODEL_DIRECTORY / "model.joblib"

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
def get_pure_test_data_service() -> IncidentService | None:
    if not PATH_TO_PURE_TEST_DATA.is_file():
        return None

    return IncidentService(IncidentRepository(PATH_TO_PURE_TEST_DATA))


@cache
def get_ml_model() -> SocCatBoostModel | None:
    if not PATH_TO_ML_MODEL_JOBLIB.is_file():
        return None

    if not PATH_TO_ML_MODEL_METADATA.is_file():
        return None

    return SocCatBoostModel(PATH_TO_MODEL_DIRECTORY)


@cache
def get_pure_test_predictions() -> pd.DataFrame | None:
    """Прогнозы модели на pure_test, None - если нет модели или выборки."""
    model = get_ml_model()
    if model is None:
        return None

    pure_test_data_service = get_pure_test_data_service()
    if pure_test_data_service is None:
        return None

    incidents = pure_test_data_service.repository.get_all()

    return build_prediction_table(
        incidents,
        model.predict_positive_probabilities(incidents),
        model.threshold,
    )


def get_incident_shap_values(entity_id: str) -> pd.DataFrame | None:
    ml_model = get_ml_model()
    pure_test_service = get_pure_test_data_service()

    if ml_model is None or pure_test_service is None:
        return None

    incidents = pure_test_service.repository.get_all()
    features = incidents.loc[incidents[Col.ID] == entity_id]

    if features.empty:
        return None

    return ml_model.get_shap_values(features)
