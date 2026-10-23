import pandas as pd
import plotly.graph_objects as go

SEVERITIES = {
    "Низкая": ["низкая", "low"],
    "Средняя": ["средняя", "medium"],
    "Высокая": ["высокая", "high"],
    "Критическая": ["критическая", "critical"],
}


COLORS = {
    "Не указана": "#F2EFED",
    "Низкая": "#DDD8D5",
    "Средняя": "#8D8683",
    "Высокая": "#B8B1AE",
    "Критическая": "#B54863",
}


PERIOD_LABELS = ["24 часа", "7 дней", "30 дней", "Год", "Весь период"]


def _normalize_df(df: pd.DataFrame) -> pd.DataFrame:
    data = df.copy()
    data["Создан"] = pd.to_datetime(data["Создан"], utc=True, errors="coerce")
    data = data.dropna(subset=["Создан"]).copy()

    severity = data["Критичность"].astype("string").str.strip().str.casefold()
    data["Уровень"] = "Не указана"

    for level, aliases in SEVERITIES.items():
        data.loc[severity.isin(aliases), "Уровень"] = level

    return data


def _get_period_bounds(df: pd.DataFrame, period: str):
    end = df["Создан"].max()

    if period == "24 часа":
        start = end - pd.Timedelta(hours=24)
    elif period == "7 дней":
        start = end - pd.Timedelta(days=7)
    elif period == "30 дней":
        start = end - pd.Timedelta(days=30)
    elif period == "Год":
        start = end - pd.DateOffset(years=1)
    else:
        start = df["Создан"].min()

    return start, end



def _choose_frequency(start, end, period=None):
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
    data = df[
        (df["Создан"] >= start)
        & (df["Создан"] < end)
    ].copy()

    start_naive = start.tz_localize(None)
    end_naive = end.tz_localize(None)

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

    data["Время"] = floor_time(
        data["Создан"].dt.tz_localize(None)
    )

    grouped = (
        data.groupby(["Время", "Уровень"])
        .size()
        .unstack(fill_value=0)
        .reindex(columns=list(COLORS), fill_value=0)
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
        return (
            f"{start:%d.%m.%Y} — "
            f"{last_day:%d.%m.%Y}"
        )

    return (
        f"{start:%d.%m.%Y %H:%M} — "
        f"{end:%d.%m.%Y %H:%M}"
    )


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
    period: str = "30 дней",
    visible_range: tuple | None = None,
):
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

    base_start, base_end = _get_period_bounds(data, period)

    start, end = base_start, base_end
    if visible_range is not None:
        vr_start, vr_end = visible_range
        start = max(base_start, vr_start)
        end = min(base_end, vr_end)

    freq = _choose_frequency(start, end, period)
    grouped = _prepare_grouped(data, start, end, freq)

    fig = go.Figure()


    # Подписи интервалов для всплывающей подсказки
    interval_labels = []

    for timestamp in grouped["Время"]:
        interval_end = _next_bucket_start(timestamp, freq)

        interval_labels.append(
            _format_interval(timestamp, interval_end, freq)
        )

    if freq == "MS":
        widths = [
            (
                _next_bucket_start(ts, freq) - ts
            ).total_seconds() * 1000 * 0.75
            for ts in grouped["Время"]
        ]
    else:
        widths = _bar_width_ms(freq)

    centers = [
        ts + (
            _next_bucket_start(ts, freq) - ts
        ) / 2
        for ts in grouped["Время"]
    ]

    for level, color in COLORS.items():
        fig.add_bar(
            x=centers,
            y=grouped[level],
            name=level,
            marker_color=color,
            width=widths,
            customdata=interval_labels,
            hovertemplate=(
                "%{customdata}"
                "<br>Инцидентов: %{y:d}"
                "<extra></extra>"
            ),
        )


    fig.update_layout(
        title=dict(
        text="Динамика новых инцидентов",
        x=0.3,
        xanchor="left",
        yanchor="top",
        font=dict(size=16),
        ),
        barmode="stack",
        bargap=0.18,
        height=310,
        margin=dict(l=35, r=15, t=25, b=60),
        hovermode="closest",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(
            orientation="h",
            x=0,
            y=-0.22,
            xanchor="left",
            yanchor="top",
        ),
        xaxis=dict(
            title=None,
            showgrid=False,
            rangeslider=dict(visible=False),
            automargin=True,
        ),
        yaxis=dict(
            title="Количество инцидентов",
            rangemode="tozero",
            gridcolor="#E8ECF0",
            zeroline=False,
            tickformat="d",
            dtick=1 if grouped[list(COLORS)].sum(axis=1).max() <= 10 else None,
            nticks=8,
            fixedrange=True,
        ),
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


def calculate_summary_stats(
    df: pd.DataFrame,
    period: str = "24 часа",
) -> dict:
    data = _normalize_df(df)

    result = {
        "new": 0,
        "critical": 0,
        "no_verdict": 0,
        "no_owner": 0,
    }

    if data.empty:
        return result

    start, end = _get_period_bounds(data, period)

    data = data[
        (data["Создан"] >= start)
        & (data["Создан"] <= end)
    ].copy()

    if data.empty:
        return result

    result["new"] = len(data)

    # Критические инциденты
    result["critical"] = int(
        (data["Уровень"] == "Критическая").sum()
    )

    # Инциденты без вердикта
    if "Вердикт" in data.columns:
        verdict = (
            data["Вердикт"]
            .astype("string")
            .str.strip()
            .str.casefold()
        )

        result["no_verdict"] = int(
            (
                verdict.isna()
                | verdict.isin([
                    "",
                    "не указан",
                    "не указано",
                    "—",
                ])
            ).sum()
        )

    # Инциденты без ответственного
    if "Ответственный" in data.columns:
        owner = (
            data["Ответственный"]
            .astype("string")
            .str.strip()
            .str.casefold()
        )

        result["no_owner"] = int(
            (
                owner.isna()
                | owner.isin([
                    "",
                    "не указан",
                    "не назначен",
                    "—",
                ])
            ).sum()
        )

    return result


def calculate_summary_comparison(
    df: pd.DataFrame,
    period: str = "24 часа",
) -> dict:
    # Текущие четыре показателя
    current = calculate_summary_stats(df, period)

    changes = {
        key: "—"
        for key in current
    }

    # Для всей истории предыдущего периода нет
    if period == "Весь период":
        return {
            "current": current,
            "changes": changes,
        }

    data = _normalize_df(df)

    if data.empty:
        return {
            "current": current,
            "changes": changes,
        }

    start, end = _get_period_bounds(data, period)

    # Предыдущий интервал той же продолжительности
    duration = end - start
    previous_start = start - duration

    previous_data = data[
        (data["Создан"] >= previous_start)
        & (data["Создан"] < start)
    ].copy()

    def count_metrics(frame):
        if frame.empty:
            return dict.fromkeys(current, 0)

        def missing_count(column, missing_values):
            if column not in frame.columns:
                return 0

            values = (
                frame[column]
                .astype("string")
                .str.strip()
                .str.casefold()
            )

            return int(
                (
                    values.isna()
                    | values.isin(missing_values)
                ).sum()
            )

        return {
            "new": len(frame),
            "critical": int(
                (frame["Уровень"] == "Критическая").sum()
            ),
            "no_verdict": missing_count(
                "Вердикт",
                ["", "не указан", "не указано", "—"],
            ),
            "no_owner": missing_count(
                "Ответственный",
                ["", "не указан", "не назначен", "—"],
            ),
        }

    previous = count_metrics(previous_data)

    for key, value in current.items():
        old_value = previous[key]

        if old_value == 0:
            # Не отображаем некорректные проценты
            changes[key] = "—"
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
