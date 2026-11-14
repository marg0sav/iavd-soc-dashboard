Запуск приложения:

```
poetry install
poetry run soc-dashboard
```

Или `poetry run python -m soc_dashboard`.

Приложение будет доступно по `http://127.0.0.1:5000/`


*Dev build/run:*
```bash
poetry run soc-dashboard --use-reloader --debug --no-run-browser
```

## ML

Для генерации метаданных для ML модели необходимо иметь исходный dataset incidents_soc.parquete + запустить [notebooks/ml.ipynb](notebooks/ml.ipynb)

## Interesting to know

Несколько ресурсов (сайтов) которые можно использовать для fast-start:
 - [from-data-to-viz](https://www.data-to-viz.com/) (Помощь выбора графика под тип данных)
 - [dataviz-inspiration](https://www.dataviz-inspiration.com) (Примеры множеств графиков на различных данных)
 - [color-brewer2](https://colorbrewer2.org/) (Помощь с палитрой цветов)
 - [dashboard-design-patterns](https://dashboarddesignpatterns.github.io/patterns.html) (Паттерны построения дашбордов)
 - [storytelling-with-data](https://www.storytellingwithdata.com/) (Как правильно презентовать отчеты)