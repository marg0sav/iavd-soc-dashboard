from enum import Enum

import pandas as pd

# Подпись и цвет для пустой или нераспознанной критичности
UNSPECIFIED = "Не указана"
UNSPECIFIED_COLOR = "#D9D9D9"


# Цвета уровней - ColorBrewer YlOrRd likely.
class Severity(Enum):
    """Уровень критичности инцидента."""

    # (подпись, приоритет, варианты написания в датасете, цвет на графике)
    # чем меньше приоритет, тем раньше инцидент в очереди
    CRITICAL = ("Критическая", 0, ("критическая", "critical"), "#800026")
    HIGH = ("Высокая", 1, ("высокая", "high"), "#E31A1C")
    MEDIUM = ("Средняя", 2, ("средняя", "medium"), "#FD8D3C")
    LOW = ("Низкая", 3, ("низкая", "low"), "#FED976")
    INFORMATIONAL = (
        "Информационная",
        4,
        ("информационная", "informational"),
        "#9ECAE1",
    )

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
