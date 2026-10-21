from pathlib import Path
import pandas as pd

class IncidentRepository:
    def __init__(self, dataset_path: str | Path):
        self.dataset_path = Path(dataset_path)
        self._df = self._load()
        
    def _load(self) -> pd.DataFrame:
        df = pd.read_parquet(self.dataset_path)
        df.columns = df.columns.astype(str).str.strip()

        if "EntityId" not in df.columns:
            raise ValueError("В датасете отсутствует столбец EntityId")

        df["EntityId"] = df["EntityId"].astype("string").str.strip()

        if df["EntityId"].isna().any() or df["EntityId"].eq("").any():
            raise ValueError("EntityId не должен быть пустым")

        if df["EntityId"].duplicated().any():
            raise ValueError("EntityId должен быть уникальным")

        for column in ("Создан", "Дата", "Дата закрытия (факт)"):
            if column in df.columns:
                df[column] = pd.to_datetime(
                    df[column],
                    format="mixed",
                    dayfirst=True,
                    errors="coerce",
                    utc=True,
                )

        return df

    def get_all(self) -> pd.DataFrame:
        return self._df.copy()

    def get_by_id(self, entity_id: str) -> dict | None:
        rows = self._df[
            self._df["EntityId"] == str(entity_id)
        ]

        if rows.empty:
            return None

        return rows.iloc[0].to_dict()
