from dataclasses import dataclass


@dataclass(frozen=True)
class MLModelTrainingData:
    """Описание данных на котором обучалась модель."""

    file: str
    rows: int


@dataclass(frozen=True)
class MLModelMetrics:
    """Метрики модели на тестовой выборке."""

    accuracy: float
    precision: float
    recall: float
    f1: float


@dataclass(frozen=True)
class MLModelConfusionMatrix:
    """Матрица ошибок на тестовой выборке при пороге threshold.

    Положительный класс - "Решён" (y=1), отрицательный - "False Positive" (y=0).
    """

    # Верно: "False Positive" предсказан как "False Positive"
    tn: int
    # Ошибка: "False Positive" предсказан как "Решён"
    fp: int
    # Ошибка: "Решён" предсказан как "False Positive"
    fn: int
    # Верно: "Решён" предсказан как "Решён"
    tp: int


@dataclass(frozen=True)
class MLModelMetadata:
    """Содержимое ml_models/verdict/metadata.json."""

    task: str
    algorithm: str
    # Время UTC
    trained_at: str
    data: MLModelTrainingData
    features: list[str]
    # Вероятность, начиная с которой прогноз - положительный класс
    threshold: float
    metrics: MLModelMetrics
    confusion_matrix: MLModelConfusionMatrix

    @classmethod
    def from_dict(cls, raw: dict) -> "MLModelMetadata":
        return cls(
            **{
                **raw,
                "data": MLModelTrainingData(**raw["data"]),
                "metrics": MLModelMetrics(**raw["metrics"]),
                "confusion_matrix": MLModelConfusionMatrix(**raw["confusion_matrix"]),
            }
        )
