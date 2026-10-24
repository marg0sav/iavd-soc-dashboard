from pathlib import Path

from src.constants import Col
from src.repository import IncidentRepository

DATASET_PATH = (
    Path(__file__).resolve().parents[2] / "data" / "iavd_1000_incidents_raw_target.parquet"
)


def test_setup_data():
    incidents = IncidentRepository(DATASET_PATH).get_all()

    # Если None нас это не устраивает.
    assert incidents is not None
    
    # Датасет скорее всего не должен быть пустым.
    assert not incidents.empty
    
    # Проверяем что в датасете есть интересующие нас колонки.
    assert {Col.ID, Col.CREATED, Col.SEVERITY} <= set(incidents.columns)
