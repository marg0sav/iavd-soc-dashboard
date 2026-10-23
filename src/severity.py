from enum import Enum

import pandas as pd


class Severity(Enum):
    """Уровень критичности инцидента."""

    # (подпись, приоритет, варианты написания в датасете)
    # чем меньше приоритет, тем раньше инцидент в очереди
    CRITICAL = ("Критическая", 0, ("критическая", "critical"))
    HIGH = ("Высокая", 1, ("высокая", "high"))
    MEDIUM = ("Средняя", 2, ("средняя", "medium"))
    LOW = ("Низкая", 3, ("низкая", "low"))
    INFORMATIONAL = ("Информационная", 4, ("информационная", "informational"))

    def __init__(self, label: str, priority: int, aliases: tuple[str, ...]):
        self.label = label
        self.priority = priority
        self.aliases = aliases


_BY_ALIAS = {
    alias: severity
    for severity in Severity
    for alias in severity.aliases
}


def parse_severity(values: pd.Series) -> pd.Series:
    """Приводит сырые значения к Severity, нераспознанные становятся NaN."""
    return (
        values
        .astype("string")
        .str.strip()
        .str.casefold()
        .map(_BY_ALIAS)
    )
