import numpy as np
import pandas as pd

from soc_dashboard.domain.columns import Col

# Вердикты бинарной задачи, как в notebooks/ml.ipynb: y=1 - "Решён"
VERDICT_RESOLVED = "Решён"
VERDICT_FALSE_POSITIVE = "False Positive"


class PredictionCol:
    """Столбцы таблицы прогнозов, которых нет в исходном датасете."""

    PROBABILITY = "Вероятность(\"Решен\"), %"
    PREDICTED = "Прогноз модели"
    ACTUAL = "Вердикт аналитика"
    RESULT = "Результат"


class PredictionResult:
    """Сравнение прогноза модели с вердиктом аналитика."""

    MATCH = "Верный прогноз"
    # Аналитик: "Решён", модель: "False Positive" - пропущен реальный инцидент
    # Аналитик: "False Positive", модель: "Решён" - лишняя работа аналитику
    FALSE_ALARM = "Ошибка модели"
    MISSED = "Пропуск"


def build_prediction_table(
    incidents: pd.DataFrame,
    probabilities: np.ndarray,
    threshold: float,
) -> pd.DataFrame:
    """Таблица прогнозов: от самых вероятных "Решён" к наименее вероятным."""
    predicted = probabilities >= threshold
    actual = incidents[Col.VERDICT].eq(VERDICT_RESOLVED).to_numpy()

    table = pd.DataFrame(
        {
            Col.ID: incidents[Col.ID].to_numpy(),
            Col.CREATED: incidents[Col.CREATED].to_numpy(),
            Col.NAME: incidents[Col.NAME].to_numpy(),
            Col.SEVERITY: incidents[Col.SEVERITY].to_numpy(),
            PredictionCol.PROBABILITY: (probabilities * 100).round(1),
            PredictionCol.PREDICTED: np.where(
                predicted, VERDICT_RESOLVED, VERDICT_FALSE_POSITIVE
            ),
            PredictionCol.ACTUAL: incidents[Col.VERDICT].to_numpy(),
            PredictionCol.RESULT: np.select(
                [predicted == actual, actual],
                [PredictionResult.MATCH, PredictionResult.MISSED],
                PredictionResult.FALSE_ALARM,
            ),
        }
    )
    return table.sort_values(
        PredictionCol.PROBABILITY, ascending=False, ignore_index=True
    )
