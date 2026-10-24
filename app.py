from pathlib import Path

from taipy.gui import Gui

from src.pages.dashboard import dashboard


def on_init(state):
    # Глобальный on_init: делегирует инициализацию сессии страницам.
    dashboard.on_init(state)


def main():
    gui = Gui(
        page=dashboard.dashboard_page,
        css_file=str(Path(__file__).resolve().parent / "styles.css"),
    )
    
    gui.on_init = on_init

    gui.run(
        title="SOC Dashboard",
        dark_mode=False,
        host="127.0.0.1",
        port=5000,
    )

if __name__ == "__main__":
    main()
