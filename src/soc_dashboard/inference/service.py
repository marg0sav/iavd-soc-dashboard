import pandas as pd
from soc_dashboard.model.catboost_model import SocCatBoostModel
from soc_dashboard.inference.inference_service import SocInferenceService
from soc_dashboard.inference.result import SocModelInferenceResult

class SocModelInferenceService(SocInferenceService):
    def __init__(self, model: SocCatBoostModel):
        self._model = model

    def predict(
        self,
        incident_id: str,
        features: pd.DataFrame,
    ) -> SocModelInferenceResult:

        probability = self._model.predict_positive_probability(features)

        verdict = (
            "Решён" if probability >= self._model.threshold
            else "False Positive"
        )

        return SocModelInferenceResult(incident_id=incident_id, verdict=verdict,
                               probability=probability)