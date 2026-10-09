from pathlib import Path
from src.repository import IncidentRepository
from src.service import IncidentService
from src.ui import create_gui


def main():
    project_dir = Path(__file__).resolve().parent

    repository = IncidentRepository(
        project_dir / "data" / "iavd_1000_incidents_raw_target.parquet"
    )

    service = IncidentService(repository)

    gui = create_gui(service)

    gui.run(
        title="SOC Dashboard",
        dark_mode=False,
        host="127.0.0.1",
        port=5000,
    )

if __name__ == "__main__":
    main()
