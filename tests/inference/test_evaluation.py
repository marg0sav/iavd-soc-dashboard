import numpy as np
import pandas as pd

from soc_dashboard.domain.columns import Col
from soc_dashboard.inference.evaluation import (
    PredictionCol,
    PredictionResult,
    build_prediction_table,
)


def test_compares_prediction_with_analyst_verdict():
    INCIDENTS = pd.DataFrame(
        {
            Col.ID: [1, 2, 3, 4],
            Col.CREATED: pd.to_datetime(["2025-01-01"] * 4, utc=True),
            Col.NAME: ["a", "b", "c", "d"],
            Col.SEVERITY: ["Высокая", "Низкая", "Средняя", "Средняя"],
            Col.VERDICT: ["Решён", "Решён", "False Positive", "False Positive"],
            # Признаки модели в таблицу не попадают
            "hour": [1, 2, 3, 4],
        }
    )
    PROBABILITIES = np.array([0.9, 0.2, 0.8, 0.1])
    
    table = build_prediction_table(INCIDENTS, PROBABILITIES, threshold=0.7)
    assert len(table) == len(INCIDENTS)
    
    predictions_status = dict(zip(table[Col.ID], table[PredictionCol.RESULT], strict=True))
    assert predictions_status == {
        1: PredictionResult.MATCH,
        2: PredictionResult.MISSED,
        3: PredictionResult.FALSE_ALARM,
        4: PredictionResult.MATCH,
    }
