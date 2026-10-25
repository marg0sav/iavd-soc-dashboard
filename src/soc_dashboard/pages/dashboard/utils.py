import re
from datetime import datetime

def format_date_input(value):
    text = str(value or "").strip()

    # Разрешаем только цифры и точки
    if not re.fullmatch(r"[0-9.]*", text):
        raise ValueError("Разрешены только цифры и точки")

    digits = text.replace(".", "")[:8]

    parts = [
        digits[:2],
        digits[2:4],
        digits[4:8],
    ]

    return ".".join(part for part in parts if part)


def parse_date_input(value):
    if not re.fullmatch(r"\d{2}\.\d{2}\.\d{4}", value):
        raise ValueError(
            "Введите дату полностью: ДД.ММ.ГГГГ"
        )

    try:
        return datetime.strptime(value, "%d.%m.%Y").date()
    except ValueError:
        raise ValueError("Указана несуществующая дата")