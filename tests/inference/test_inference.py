import pandas as pd
from soc_dashboard.inference.service import SocModelInferenceService

class StubModel:
    threshold = 0.7
    def predict_positive_probability(self, features):
        return 0.85

def test_inference():
    service = SocModelInferenceService(StubModel())
    result = service.predict("123", pd.DataFrame())

    assert result.verdict == "Решён"