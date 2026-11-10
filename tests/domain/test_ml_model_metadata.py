import json

from soc_dashboard.domain.ml_model_metadata import (
    MLModelMetadata,
    MLModelMetrics,
    MLModelTrainingData,
)

# Пример содержимого metadata.json
METADATA_JSON = """
{
  "task": "Решён или False Positive",
  "algorithm": "CatBoostClassifier",
  "trained_at": "2026-11-08T16:55:31+00:00",
  "data": {
    "file": "iavd_ml_dataset.parquet",
    "rows": 196969
  },
  "features": [
    "Критичность",
    "hour"
  ],
  "threshold": 0.7,
  "metrics": {
    "accuracy": 0.8795,
    "precision": 0.5988,
    "recall": 0.6683,
    "f1": 0.6316
  }
}
"""


def test_reads_metadata_json():
    metadata = MLModelMetadata.from_dict(json.loads(METADATA_JSON))

    assert metadata == MLModelMetadata(
        task="Решён или False Positive",
        algorithm="CatBoostClassifier",
        trained_at="2026-11-08T16:55:31+00:00",
        data=MLModelTrainingData(file="iavd_ml_dataset.parquet", rows=196969),
        features=["Критичность", "hour"],
        threshold=0.7,
        metrics=MLModelMetrics(
            accuracy=0.8795,
            precision=0.5988,
            recall=0.6683,
            f1=0.6316,
        ),
    )
