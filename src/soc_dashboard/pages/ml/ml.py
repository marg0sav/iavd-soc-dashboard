import taipy.gui.builder as tgb

with tgb.Page() as ml_page, tgb.part(class_name="soc-dashboard"):
    tgb.text("## Модель", mode="md")
