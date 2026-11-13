import json

import joblib
import pandas as pd
import pytest
from catboost import CatBoostClassifier

from soc_dashboard.model.catboost_model import SocCatBoostModel


@pytest.fixture
def artifact_dir(tmp_path):
    """Очень малеьнкая модель: model.joblib + metadata.json."""
    features = pd.DataFrame(
        {
            "Критичность": ["Высокая", "Низкая", "Высокая", "Низкая"],
            "hour": [1, 2, 3, 4],
        }
    )
    model = CatBoostClassifier(
        iterations=5, verbose=False, cat_features=["Критичность"]
    )

    model.fit(
        features, [1, 0, 1, 0]
    )  # 1 - "Решен" (Реальный инцидент), 0 "False Positive" (ложный инцидент)

    joblib.dump(model, tmp_path / "model.joblib")
    (tmp_path / "metadata.json").write_text(
        json.dumps({"threshold": 0.7}), encoding="utf-8"
    )

    return tmp_path


def test_model_loading(artifact_dir):
    model = SocCatBoostModel(artifact_dir)

    assert model.feature_names == ["Критичность", "hour"]
    assert model.categorical_features == ["Критичность"]
    assert model.threshold == 0.7


def test_predict_positive_probability(artifact_dir):
    model = SocCatBoostModel(artifact_dir)
    features = pd.DataFrame({"Критичность": ["Высокая"], "hour": [1]})

    assert 0 <= model.predict_positive_probability(features) <= 1
