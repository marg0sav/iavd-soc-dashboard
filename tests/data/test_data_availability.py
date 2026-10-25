from soc_dashboard.constants import Col
from soc_dashboard.data.data import PATH_TO_DATA
from soc_dashboard.repository import IncidentRepository


def test_setup_data():
    incidents = IncidentRepository(PATH_TO_DATA).get_all()

    # Если None нас это не устраивает.
    assert incidents is not None
    
    # Датасет скорее всего не должен быть пустым.
    assert not incidents.empty
    
    # Проверяем что в датасете есть интересующие нас колонки.
    assert {Col.ID, Col.CREATED, Col.SEVERITY} <= set(incidents.columns)
