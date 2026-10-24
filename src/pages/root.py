import taipy.gui.builder as tgb

# Корневая страница: является header'ом для всех страниц приложения.
with tgb.Page() as root_page:
    with tgb.layout(columns="1 auto"):
        tgb.text("**SOC** Dashboard", mode="md")

        tgb.navbar(
            lov=[
                ("/dashboard", "Дашборд"),
            ],
        )

    # Содержимое текущей страницы Taipy подставляет на место tgb.content().
    tgb.content()
