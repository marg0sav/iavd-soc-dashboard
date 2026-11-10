import json

import pytest

from soc_dashboard.data import data
from soc_dashboard.domain.ml_model_metadata import MLModelMetadata

METADATA = {
    "task": "Решён или False Positive",
    "algorithm": "CatBoostClassifier",
    "trained_at": "2026-11-08T16:55:31+00:00",
    "data": {"file": "iavd_ml_dataset.parquet", "rows": 196969},
    "features": ["Критичность", "hour"],
    "threshold": 0.7,
    "metrics": {
        "accuracy": 0.8795,
        "precision": 0.5988,
        "recall": 0.6683,
        "f1": 0.6316,
    },
}


@pytest.fixture
def metadata_path(tmp_path, monkeypatch):
    # Делаем mock-данные вместо реальных и подменяем реальный путь через monkeypatch.
    path = tmp_path / "metadata.json"
    monkeypatch.setattr(data, "PATH_TO_ML_MODEL_METADATA", path)

    # @cache запоминает результат между тестами. Чистим его.
    data.get_ml_model_metadata.cache_clear()
    yield path
    data.get_ml_model_metadata.cache_clear()


def test_returns_none_without_file(metadata_path):
    assert data.get_ml_model_metadata() is None


def test_reads_metadata_file(metadata_path):
    metadata_path.write_text(json.dumps(METADATA, ensure_ascii=False), encoding="utf-8")

    assert data.get_ml_model_metadata() == MLModelMetadata.from_dict(METADATA)
