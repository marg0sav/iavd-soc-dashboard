from datetime import datetime

import taipy.gui.builder as tgb

from soc_dashboard.analytics import build_confusion_matrix_figure
from soc_dashboard.data.data import (
    get_ml_model_metadata,
    get_pure_test_predictions,
    get_pure_test_data_service,
)
from soc_dashboard.domain.columns import Col
from soc_dashboard.inference.evaluation import PredictionCol, PredictionResult
from soc_dashboard.service import empty_card

# Метаданные статичны и читаются один раз при запуске,
# поэтому страница строится из готовых значений, без переменных состояния
ml_model_metadata = get_ml_model_metadata()

# Если метаданные не получилось считать, то не строим Confusion matrix
confusion_figure = (
    None
    if ml_model_metadata is None
    else build_confusion_matrix_figure(ml_model_metadata.confusion_matrix)
)
# Выключаем plotly инстурменты.
confusion_chart_config = {"displayModeBar": False, "responsive": True}

# Прогнозы на pure_test считаются один раз при запуске
pure_test_df = get_pure_test_predictions()

# Подсветка строк, где модель ошиблась
PREDICTION_ROW_CLASSES = {
    PredictionResult.MISSED: "prediction-missed",
    PredictionResult.FALSE_ALARM: "prediction-false",
}


def prediction_row_class(state, index, row):
    return PREDICTION_ROW_CLASSES.get(row[PredictionCol.RESULT], "")


# Карточка инцидента по клику на строку: так же, как в очереди дашборда
card_df = empty_card()
card_open = False
selected_title = "Выберите инцидент"


def load_incident(state, entity_id):
    state.card_df = get_pure_test_data_service().get_card(entity_id)
    state.selected_title = f"Инцидент {entity_id}"


def on_row_selected(state, var_name, payload):
    index = payload.get("index")

    if index in state.pure_test_df.index:
        entity_id = state.pure_test_df.loc[index, Col.ID]
        load_incident(state, entity_id)
        state.card_open = True


def close_card(state):
    state.card_open = False


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

            with tgb.part(class_name="soc-panel soc-ml-confusion"):
                with tgb.part(class_name="soc-toolbar"):
                    tgb.text("## Матрица ошибок:", mode="md")

                tgb.chart(
                    figure="{confusion_figure}",
                    width="100%",
                    height="260px",
                    plot_config="{confusion_chart_config}",
                )
                tgb.text(
                    f"(Тестовая выборка, порог={ml_model_metadata.threshold})",
                    class_name="soc-panel-note",
                )

        with tgb.part(class_name="soc-panel"):
            with tgb.part(class_name="soc-toolbar"):
                tgb.text("## Прогнозы на отложенной выборке:", mode="md")

            if pure_test_df is None:
                tgb.text("Нет модели или выборки для расчета.")
            else:
                tgb.table(
                    "{pure_test_df}",
                    editable=False,
                    filter=True,
                    page_size=100,
                    page_size_options=[20, 100, 250, 500],
                    width="100%",
                    height="520px",
                    date_format="dd.MM.yyyy HH:mm",
                    on_action=on_row_selected,
                    row_class_name=prediction_row_class,
                    class_name="soc-ml-predictions",
                )

    with tgb.dialog(
        "{card_open}",
        title="Карточка инцидента",
        width="850px",
        labels=["Закрыть"],
        on_action=close_card,
    ):
        tgb.text("{selected_title}")
        tgb.table("{card_df}", editable=False, page_size=20, width="100%")
