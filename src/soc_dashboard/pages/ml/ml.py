from datetime import datetime

import taipy.gui.builder as tgb

from soc_dashboard.data.data import get_ml_model_metadata

# Метаданные статичны и читаются один раз при запуске,
# поэтому страница строится из готовых значений, без переменных состояния
ml_model_metadata = get_ml_model_metadata()

with tgb.Page() as ml_page, tgb.part(class_name="soc-dashboard"):
    with tgb.part(class_name="soc-toolbar"):
        tgb.text("## Модель", mode="md")

    if ml_model_metadata is None:
        tgb.text("Модель не обучена/отсутвуют метаданные модели.")
    else:
        with tgb.part(class_name="soc-metrics"):
            for label, value in (
                ("Accuracy", ml_model_metadata.metrics.accuracy),
                ("Precision", ml_model_metadata.metrics.precision),
                ("Recall", ml_model_metadata.metrics.recall),
                ("F1", ml_model_metadata.metrics.f1),
            ):
                with tgb.part(class_name="soc-metric"):
                    tgb.text(label, class_name="metric-label")
                    tgb.text(value, class_name="metric-value")

            with tgb.part(class_name="soc-panel soc-ml-list"):
                with tgb.part(class_name="soc-toolbar"):
                    tgb.text("## Метаданные модели:", mode="md")

                # Оставляем метаданные на уровне soc-panel.
                trained_at = datetime.fromisoformat(ml_model_metadata.trained_at)
                # 196969 -> 196 969
                # TODO: вынести куда нибудь ?
                rows = f"{ml_model_metadata.data.rows:,}".replace(",", " ")

                tgb.text(
                    f"- **Название задачи:** {ml_model_metadata.task}\n"
                    f"- **Алгоритм модели:** {ml_model_metadata.algorithm}\n"
                    f"- **Обучена:** {trained_at:%d.%m.%Y %H:%M} UTC\n"
                    f"- **Размер выборки:** {rows}\n"
                    f"- **Датасет:** {ml_model_metadata.data.file}\n"
                    f"- **Порог:** {ml_model_metadata.threshold}",
                    mode="md",
                )
