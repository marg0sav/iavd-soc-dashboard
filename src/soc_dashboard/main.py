from pathlib import Path

from taipy.gui import Gui

from soc_dashboard.pages.dashboard import dashboard
from soc_dashboard.pages.root import root_page

# "/" — root-страница с header'ом; на root-странице Taipy показывает первую страницу 
# после неё (dashboard_page).
pages = {
    "/": root_page,
    "dashboard": dashboard.dashboard_page,
}


def on_init(state):
    # Глобальный on_init: делегирует инициализацию сессии страницам.
    dashboard.on_init(state)


def main():
    gui = Gui(
        pages=pages,
        css_file="assets/styles.css",
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
