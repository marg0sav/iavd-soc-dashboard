from enum import Enum

import pandas as pd


# Подпись и цвет для пустой или нераспознанной критичности
UNSPECIFIED = "Не указана"
UNSPECIFIED_COLOR = "#F2EFED"

class Severity(Enum):
    """Уровень критичности инцидента."""

    # (подпись, приоритет, варианты написания в датасете, цвет на графике)
    # чем меньше приоритет, тем раньше инцидент в очереди
    CRITICAL = ("Критическая", 0, ("критическая", "critical"), "#B54863")
    HIGH = ("Высокая", 1, ("высокая", "high"), "#B8B1AE")
    MEDIUM = ("Средняя", 2, ("средняя", "medium"), "#8D8683")
    LOW = ("Низкая", 3, ("низкая", "low"), "#DDD8D5")
    INFORMATIONAL = ("Информационная", 4, ("информационная", "informational"), "#E8E4E1")

    def __init__(self, label: str, priority: int, aliases: tuple[str, ...], color: str):
        self.label = label
        self.priority = priority
        self.aliases = aliases
        self.color = color

SEVERITY_COLORS = {
    UNSPECIFIED: UNSPECIFIED_COLOR,
    # Распаковка списка "название" : цвет.
    **{severity.label: severity.color for severity in reversed(Severity)},
}


_BY_ALIAS = {alias: severity for severity in Severity for alias in severity.aliases}


def parse_severity(values: pd.Series) -> pd.Series:
    """Приводит сырые значения к Severity, нераспознанные становятся NaN."""
    return values.astype("string").str.strip().str.casefold().map(_BY_ALIAS)
