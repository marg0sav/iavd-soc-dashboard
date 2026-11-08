Запуск приложения:

```
poetry install
poetry run soc-dashboard
```

Или `poetry run python -m soc_dashboard`.

Приложение будет доступно по `http://127.0.0.1:5000/`

## ML

Для генерации метаданных для ML модели необходимо иметь исходный dataset incidents_soc.parquete + запустить [notebooks/ml.ipynb](notebooks/ml.ipynb)