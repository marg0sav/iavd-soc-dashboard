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

    @classmethod
    def from_dict(cls, raw: dict) -> "MLModelMetadata":
        return cls(
            **{
                **raw,
                "data": MLModelTrainingData(**raw["data"]),
                "metrics": MLModelMetrics(**raw["metrics"]),
            }
        )
