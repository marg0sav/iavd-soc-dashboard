from unittest.mock import Mock
import pandas as pd
from soc_dashboard.inference.service import InferenceService

def test_inference():

    model = Mock()
    model.threshold = 0.7
    model.predict_positive_probability.return_value = 0.85
    service = InferenceService(model)
    result = service.predict("123", pd.DataFrame())

    assert result.incident_id == "123"
    assert result.verdict == "Решён"
    assert result.probability == 0.85