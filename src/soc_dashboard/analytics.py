from datetime import date
from html import escape
from textwrap import shorten, wrap

import pandas as pd
import plotly.graph_objects as go

from soc_dashboard.constants import NO_DATA
from soc_dashboard.domain.columns import Col
from soc_dashboard.domain.ml_model_metadata import MLModelConfusionMatrix
from soc_dashboard.domain.period import Period
from soc_dashboard.domain.severity import (
    SEVERITY_COLORS,
    UNSPECIFIED,
    Severity,
    parse_severity,
)


def _normalize_df(df: pd.DataFrame) -> pd.DataFrame:
    data = df.copy()
    data[Col.CREATED] = pd.to_datetime(data[Col.CREATED], utc=True, errors="coerce")
    data = data.dropna(subset=[Col.CREATED]).copy()

    data["Уровень"] = (
        parse_severity(data[Col.SEVERITY])
        .map(lambda s: s.label, na_action="ignore")
        .fillna(UNSPECIFIED)
    )

    return data


def _get_period_bounds(df: pd.DataFrame, period: str):
    end = df[Col.CREATED].max()

    if period == "24 часа":
        start = end - pd.Timedelta(hours=24)
    elif period == "7 дней":
        start = end - pd.Timedelta(days=7)
    elif period == "30 дней":
        start = end - pd.Timedelta(days=30)
    elif period == "Год":
        start = end - pd.DateOffset(years=1)
    else:
        start = df[Col.CREATED].min()

    return start, end


def _choose_frequency(start, end):
    hours = (end - start).total_seconds() / 3600
    days = hours / 24

    if hours <= 1:
        return "5min"

    if hours <= 12:
        return "15min"

    if days <= 7:
        return "h"

    if days < 183:
        return "D"

    if days < 730:
        return "W-MON"

    return "MS"


def _prepare_grouped(df, start, end, freq):
    data = df[(df[Col.CREATED] >= start) & (df[Col.CREATED] < end)].copy()

    start_naive = start.tz_localize(None)
    # end не входит в интервал: последний столбец - тот, где лежит момент перед end
    end_naive = (end - pd.Timedelta(microseconds=1)).tz_localize(None)

    # Используем начало интервала как временную метку.
    if freq == "MS":
        first = start_naive.to_period("M").start_time
        last = end_naive.to_period("M").start_time

        def floor_time(s):
            return s.dt.to_period("M").dt.start_time

    elif freq == "W-MON":
        first = start_naive.to_period("W-SUN").start_time
        last = end_naive.to_period("W-SUN").start_time

        def floor_time(s):
            return s.dt.to_period("W-SUN").dt.start_time

    else:
        first = start_naive.floor(freq)
        last = end_naive.floor(freq)

        def floor_time(s):
            return s.dt.floor(freq)

    timeline = pd.date_range(
        first,
        last,
        freq="7D" if freq == "W-MON" else freq,
    )

    data["Время"] = floor_time(data[Col.CREATED].dt.tz_localize(None))

    grouped = (
        data.groupby(["Время", "Уровень"])
        .size()
        .unstack(fill_value=0)
        .reindex(columns=list(SEVERITY_COLORS), fill_value=0)
        .reindex(timeline, fill_value=0)
    )

    grouped.index.name = "Время"

    return grouped.reset_index()


def _next_bucket_start(start, freq):
    durations = {
        "5min": pd.Timedelta(minutes=5),
        "15min": pd.Timedelta(minutes=15),
        "h": pd.Timedelta(hours=1),
        "D": pd.Timedelta(days=1),
        "W-MON": pd.Timedelta(days=7),
    }

    if freq == "MS":
        return start + pd.DateOffset(months=1)

    return start + durations[freq]


def _format_interval(start, end, freq):
    if freq == "MS":
        return start.strftime("%m.%Y")

    if freq in ("D", "W-MON"):
        last_day = end - pd.Timedelta(days=1)
        return f"{start:%d.%m.%Y} — {last_day:%d.%m.%Y}"

    return f"{start:%d.%m.%Y %H:%M} — {end:%d.%m.%Y %H:%M}"


def _bar_width_ms(freq):
    widths = {
        "5min": 5 * 60 * 1000,
        "15min": 15 * 60 * 1000,
        "h": 60 * 60 * 1000,
        "D": 24 * 60 * 60 * 1000,
        "W-MON": 7 * 24 * 60 * 60 * 1000,
    }

    if freq == "MS":
        return None

    return widths[freq] * 0.75


def build_incident_chart(
    df: pd.DataFrame,
    date_from: date,
    date_to: date,
    visible_range: tuple | None = None,
):
    """Динамика инцидентов за даты [date_from, date_to], обе включительно."""
    data = _normalize_df(df)

    if data.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Нет данных для отображения",
            x=0.5,
            y=0.5,
            xref="paper",
            yref="paper",
            showarrow=False,
        )
        return fig

    base_start = pd.Timestamp(date_from, tz="UTC")
    # Последний выбранный день включается целиком
    base_end = pd.Timestamp(date_to, tz="UTC") + pd.Timedelta(days=1)

    start, end = base_start, base_end
    if visible_range is not None:
        vr_start, vr_end = visible_range
        start = max(base_start, vr_start)
        end = min(base_end, vr_end)

    freq = _choose_frequency(start, end)
    grouped = _prepare_grouped(data, start, end, freq)

    fig = go.Figure()

    # Подписи интервалов для всплывающей подсказки
    interval_labels = []

    for timestamp in grouped["Время"]:
        interval_end = _next_bucket_start(timestamp, freq)

        interval_labels.append(_format_interval(timestamp, interval_end, freq))

    if freq == "MS":
        widths = [
            (_next_bucket_start(ts, freq) - ts).total_seconds() * 1000 * 0.75
            for ts in grouped["Время"]
        ]
    else:
        widths = _bar_width_ms(freq)

    centers = [ts + (_next_bucket_start(ts, freq) - ts) / 2 for ts in grouped["Время"]]

    for level, color in SEVERITY_COLORS.items():
        fig.add_bar(
            x=centers,
            y=grouped[level],
            name=level,
            marker_color=color,
            width=widths,
            customdata=interval_labels,
            hovertemplate=("%{customdata}<br>Инцидентов: %{y:d}<extra></extra>"),
        )

    fig.update_layout(
        barmode="stack",
        bargap=0.18,
        autosize=True,
        margin={"l": 40, "r": 20, "t": 20, "b": 54},
        hovermode="closest",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend={
            "orientation": "h",
            "x": 0,
            "y": -0.13,
            "xanchor": "left",
            "yanchor": "top",
        },
        xaxis={
            "title": None,
            "showgrid": False,
            "rangeslider": {"visible": False},
            "automargin": True,
        },
        yaxis={
            "title": "Количество инцидентов",
            "rangemode": "tozero",
            "gridcolor": "#E8ECF0",
            "zeroline": False,
            "tickformat": "d",
            "dtick": 1
            if grouped[list(SEVERITY_COLORS)].sum(axis=1).max() <= 10
            else None,
            "nticks": 8,
            "fixedrange": True,
        },
        dragmode="zoom",
        showlegend=True,
    )

    if visible_range is not None:
        display_start, display_end = visible_range
    else:
        display_start, display_end = base_start, base_end

    fig.update_xaxes(
        type="date",
        range=[
            display_start.tz_localize(None),
            display_end.tz_localize(None),
        ],
        autorange=False,
    )

    return fig


def extract_visible_range(payload: dict):
    if not payload:
        return None

    # Двойной клик / reset axes
    if payload.get("xaxis.autorange") is True:
        return None

    start = payload.get("xaxis.range[0]")
    end = payload.get("xaxis.range[1]")

    if start is None or end is None:
        rng = payload.get("xaxis.range")
        if isinstance(rng, (list, tuple)) and len(rng) == 2:
            start, end = rng

    if start is None or end is None:
        return None

    start = pd.to_datetime(start, utc=True, errors="coerce")
    end = pd.to_datetime(end, utc=True, errors="coerce")

    if pd.isna(start) or pd.isna(end):
        return None

    return start, end


# -----------------------------------------
# Краткая статистика
# -----------------------------------------

SUMMARY_MISSING_VALUES = {
    "",
    "не указан",
}


def _count_missing(df: pd.DataFrame, column: str) -> int:
    if column not in df.columns:
        return 0

    values = df[column].astype("string").str.strip().str.casefold()

    return int((values.isna() | values.isin(SUMMARY_MISSING_VALUES)).sum())


def _count_summary_metrics(data: pd.DataFrame) -> dict:
    if data.empty:
        return {
            "new": 0,
            "critical": 0,
            "no_verdict": 0,
            "no_owner": 0,
        }

    return {
        "new": len(data),
        "critical": int((data["Уровень"] == Severity.CRITICAL.label).sum()),
        "no_verdict": _count_missing(
            data,
            Col.VERDICT,
        ),
        "no_owner": _count_missing(
            data,
            Col.ASSIGNEE,
        ),
    }


def calculate_summary_comparison(
    df: pd.DataFrame,
    period: str = Period.DAY,
    date_from=None,
    date_to=None,
) -> dict:

    data = _normalize_df(df)

    empty = _count_summary_metrics(data.iloc[0:0])
    changes = {key: NO_DATA for key in empty}

    if data.empty:
        return {
            "current": empty,
            "changes": changes,
        }

    custom_range = date_from is not None and date_to is not None

    if custom_range:
        start = pd.Timestamp(date_from).tz_localize("UTC")
        end = pd.Timestamp(date_to).tz_localize("UTC") + pd.Timedelta(days=1)
    else:
        start, end = _get_period_bounds(data, period)

    # Текущий период
    current_data = data[
        (data[Col.CREATED] >= start)
        & ((data[Col.CREATED] < end) if custom_range else (data[Col.CREATED] <= end))
    ]

    current = _count_summary_metrics(current_data)

    if period == Period.ALL_TIME and not custom_range:
        return {
            "current": current,
            "changes": changes,
        }

    # Предыдущий период той же продолжительности
    duration = end - start
    previous_start = start - duration

    previous_data = data[
        (data[Col.CREATED] >= previous_start) & (data[Col.CREATED] < start)
    ]

    previous = _count_summary_metrics(previous_data)

    # Процентные изменения
    for key, value in current.items():
        old_value = previous[key]

        if old_value == 0:
            changes[key] = NO_DATA
            continue

        difference = (value - old_value) / old_value * 100

        if difference > 0:
            arrow = "↑"
        elif difference < 0:
            arrow = "↓"
        else:
            arrow = "→"

        changes[key] = f"{arrow} {abs(difference):.0f}%"

    return {
        "current": current,
        "changes": changes,
    }


def _overview_values(data, column, missing_label):
    values = data.get(
        column,
        pd.Series(pd.NA, index=data.index, dtype="string"),
    )
    values = values.astype("string").str.strip()

    missing = values.isna() | values.str.casefold().isin(SUMMARY_MISSING_VALUES)

    return values.mask(missing, missing_label)


def _format_wait(seconds):
    if pd.isna(seconds):
        return NO_DATA

    seconds = round(seconds)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)

    if days:
        return f"{days} д {hours} ч"
    if hours:
        return f"{hours} ч {minutes} мин"
    if minutes:
        return f"{minutes} мин {seconds} с"

    return f"{seconds} с"


def _overview_bar(values, total, limit=None):
    counts = values.value_counts()

    if limit is not None:
        counts = counts.head(limit)

    fig = go.Figure()
    fig.update_layout(
        autosize=True,
        margin={"l": 145, "r": 8, "t": 8, "b": 8},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={
            "family": "Arial, sans-serif",
            "size": 11,
            "color": "#625c5a",
        },
        showlegend=False,
        bargap=0.48,
        xaxis={"visible": False, "fixedrange": True},
        yaxis={
            "fixedrange": True,
            "autorange": "reversed",
            "showgrid": False,
        },
    )

    if counts.empty:
        fig.update_layout(margin={"l": 8, "r": 8, "t": 8, "b": 8})
        fig.update_yaxes(visible=False)
        fig.add_annotation(
            text="Нет данных за период",
            x=0.5,
            y=0.5,
            xref="paper",
            yref="paper",
            showarrow=False,
        )
        return fig

    labels = counts.index.astype(str).tolist()

    ticktext = [
        "<br>".join(
            escape(line)
            for line in wrap(
                shorten(label, width=38, placeholder="…"),
                width=20,
            )
        )
        for label in labels
    ]

    fig.add_bar(
        x=counts.tolist(),
        y=labels,
        orientation="h",
        marker_color=[
            "#DDD8D5" if label in {"Без вердикта", "Не указан"} else "#8D8683"
            for label in labels
        ],
        text=[str(count) for count in counts],
        textposition="outside",
        cliponaxis=False,
        customdata=[escape(label) for label in labels],
        hovertemplate=("%{customdata}<br>Карточек: %{x:d}<extra></extra>"),
    )

    fig.update_xaxes(range=[0, int(counts.max()) * 1.7])
    fig.update_yaxes(
        tickvals=labels,
        ticktext=ticktext,
        type="category",
    )

    return fig


def build_dashboard_overview(
    df,
    period=Period.DAY,
    date_from=None,
    date_to=None,
):
    data = _normalize_df(df)

    if not data.empty:
        if date_from is not None and date_to is not None:
            start = pd.Timestamp(date_from).tz_localize("UTC")
            end = pd.Timestamp(date_to).tz_localize("UTC") + pd.Timedelta(days=1)

            # Последний выбранный день включается полностью
            data = data[(data[Col.CREATED] >= start) & (data[Col.CREATED] < end)]
        else:
            start, end = _get_period_bounds(data, period)
            data = data[data[Col.CREATED].between(start, end)]

    total = len(data)

    flags = (
        _overview_values(data, Col.SLA_TAKE_OVERDUE, "")
        .str.casefold()
        .map(
            {
                "true": True,
                "1": True,
                "1.0": True,
                "да": True,
                "false": False,
                "0": False,
                "0.0": False,
                "нет": False,
            }
        )
    )

    known = int(flags.notna().sum())
    overdue = int(flags.eq(True).sum())

    taken = pd.to_datetime(
        data.get(
            Col.TAKEN_AT,
            pd.Series(pd.NaT, index=data.index),
        ),
        format="mixed",
        dayfirst=True,
        utc=True,
        errors="coerce",
    )

    seconds = (taken - data[Col.CREATED]).dt.total_seconds()

    # Пропуски и взятие в работу раньше создания исключаются
    valid = seconds[seconds.notna() & seconds.ge(0)]

    return {
        "sla_value": str(overdue) if known else NO_DATA,
        "sla_note": (
            f"{overdue / known:.1%} среди {known} карточек с известным SLA"
            if known
            else "Нет заполненного SLA"
        ),
        "take_value": (_format_wait(valid.median()) if not valid.empty else NO_DATA),
        "take_note": f"Медиана по {len(valid)} из {total} карточек",
        "types_figure": _overview_bar(
            _overview_values(data, Col.INCIDENT_TYPE, "Не указан"),
            total,
            limit=5,
        ),
        "verdicts_figure": _overview_bar(
            _overview_values(data, Col.VERDICT, "Без вердикта"),
            total,
        ),
    }


def build_confusion_matrix_figure(cm: MLModelConfusionMatrix) -> go.Figure:
    labels = ["Решён", "False Positive"]
    counts = [[cm.tp, cm.fn], [cm.fp, cm.tn]]
    shares = [[value / max(sum(row), 1) for value in row] for row in counts]
    
    # 22114 -> 22 114
    texts = [[f"{value:,}".replace(",", " ") for value in row] for row in counts]

    fig = go.Figure(
        go.Heatmap(
            z=shares,
            x=labels,
            y=labels,
            text=texts,
            zmin=0,
            zmax=1,
            colorscale="Blues",
            showscale=False,
            texttemplate="%{text}<br>%{z:.0%}",
            textfont={"size": 14},
            hovertemplate=(
                "Факт: %{y}<br>Прогноз: %{x}<br>"
                "Инцидентов: %{text}<br>Доля от факта: %{z:.1%}<extra></extra>"
            ),
        )
    )
    fig.update_layout(
        autosize=True,
        margin={"l": 8, "r": 8, "t": 8, "b": 8},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"family": "Arial, sans-serif", "size": 12, "color": "#625c5a"},
        xaxis={"title": {"text": "Прогноз модели"}, "side": "top", "fixedrange": True},
        yaxis={"title": {"text": "Реальное значение"}, "autorange": "reversed", "fixedrange": True},
    )
    return fig
