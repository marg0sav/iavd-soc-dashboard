from pathlib import Path
import pandas as pd
from soc_dashboard.constants import Col, DATETIME_COLUMNS

class IncidentRepository:
    def __init__(self, dataset_path: str | Path):
        self.dataset_path = Path(dataset_path)
        self._df = self._load()
        
    def _load(self) -> pd.DataFrame:
        df = pd.read_parquet(self.dataset_path)
        df.columns = df.columns.astype(str).str.strip()

        if Col.ID not in df.columns:
            raise ValueError(f"В датасете отсутствует столбец {Col.ID}")

        df[Col.ID] = df[Col.ID].astype("string").str.strip()

        if df[Col.ID].isna().any() or df[Col.ID].eq("").any():
            raise ValueError(f"{Col.ID} не должен быть пустым")

        if df[Col.ID].duplicated().any():
            raise ValueError(f"{Col.ID} должен быть уникальным")

        for column in DATETIME_COLUMNS:
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
            self._df[Col.ID] == str(entity_id)
        ]

        if rows.empty:
            return None

        return rows.iloc[0].to_dict()
