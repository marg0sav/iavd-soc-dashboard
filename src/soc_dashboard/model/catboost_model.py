import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from catboost import Pool

_FEATURE_LABELS = {
    "categoryMain": "Основная категория события",
    "categoryLow": "Категория нижнего уровня",
    "categoryHigh": "Категория верхнего уровня",
    "Команда": "Командная строка",
    "Имя файла-IRP": "Имя файла в карточке IRP",
    "Файловый ресурс": "Файловый объект события",
    "object.name": "Имя объекта события",
    "object": "Тип объекта события",
    "processName": "Имя процесса",
    "commandName": "Имя утилиты из команды",
}

_INPUT_ALIASES = _FEATURE_LABELS | {
    label: name for name, label in _FEATURE_LABELS.items()
}


class SocCatBoostModel:
    def __init__(self, artifact_dir: Path):

        directory = artifact_dir
        metadata = json.loads((directory / "metadata.json").read_text(encoding="utf-8"))
        self._model = joblib.load(directory / "model.joblib")
        self._feature_names = list(self._model.feature_names_)

        self._categorical_features = [
            self._feature_names[i] for i in self._model.get_cat_feature_indices()
        ]
        self._text_features = [
            self._feature_names[i] for i in self._model.get_text_feature_indices()
        ]

        classes = list(self._model.classes_)
        self._positive_index = classes.index(1)
        self._threshold = float(metadata["threshold"])

    @property
    def feature_names(self) -> list[str]:
        return self._feature_names.copy()

    @property
    def categorical_features(self) -> list[str]:
        return self._categorical_features.copy()

    @property
    def threshold(self) -> float:
        return self._threshold

    def predict_positive_probability(self, features: pd.DataFrame) -> float:
        return float(self.predict_positive_probabilities(features)[0])

    def predict_positive_probabilities(self, features: pd.DataFrame) -> np.ndarray:
        """Вероятность класса "Решён" для каждой строки features."""
        # Лишние столбцы отбрасываем, порядок - как при обучении
        return self._model.predict_proba(self._make_pool(features))[
            :, self._positive_index
        ]

    def get_shap_values(self, features: pd.DataFrame) -> pd.DataFrame:

        pool = Pool(
            features[self._feature_names], cat_features=self._categorical_features
        )
        shap_value = self._model.get_feature_importance(pool, type="ShapValues")[0]

        return pd.DataFrame(
            {"features": self._feature_names, "shap_values": shap_value[:-1]}
        )
