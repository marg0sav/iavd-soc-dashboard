import pandas as pd
from soc_dashboard.model.catboost_model import CatBoostModel
from soc_dashboard.inference.result import InferenceResult

class InferenceService:
    def __init__(self, model: CatBoostModel):
        self._model = model

    def predict(
        self,
        incident_id: str,
        features: pd.DataFrame,
    ) -> InferenceResult:

        probability = self._model.predict_positive_probability(features)

        verdict = (
            "Решён" if probability >= self._model.threshold
            else "False Positive"
        )

        return InferenceResult(incident_id=incident_id, verdict=verdict,
                               probability=probability)