# Celery + Django: асинхронные задачи

Небольшой пример того, как вынести долгую операцию из HTTP-запроса в фоновую
задачу Celery и потом забрать результат по идентификатору. Django + DRF в роли
API, Celery поверх Redis — брокер и хранилище результатов.

Смысл простой: если считать что-то тяжёлое прямо в обработчике, клиент висит и
воркер занят. Вместо этого запрос ставит задачу в очередь и сразу отдаёт
`task_id`, а результат клиент забирает отдельным запросом, когда тот готов.

## Стек

- Python, Django 3.2, Django REST Framework
- Celery 5
- Redis (брокер + result backend)

## Как работает

- `task/tasks.py` — `calculate_metric`: имитация долгого вычисления (миллионы
  итераций). Обёрнута в `@shared_task`, то есть уходит в Celery-воркер, а не
  считается в веб-процессе.
- `task/views.py` — два эндпоинта:
  - `PUT /api/launch` — ставит задачу в очередь (`.delay()`), возвращает `task_id`.
  - `GET /api/get_result?job_id=<id>` — отдаёт статус задачи (`PENDING` /
    `SUCCESS` / ...) и результат, когда он готов.
- `celery_example/celery.py` — инициализация Celery-приложения, автопоиск задач
  по приложениям Django.

## Запуск

Нужен запущенный Redis (`redis-server` или через Docker).

```bash
pip install -r requirements.txt
cp .env.example .env          # при желании поправить переменные

python manage.py migrate

# в одном терминале — Celery-воркер
celery -A celery_example worker -l info

# в другом — Django
python manage.py runserver
```

Проверка:

```bash
# запустить задачу — вернётся task_id
curl -X PUT http://127.0.0.1:8000/api/launch

# забрать результат по id
curl "http://127.0.0.1:8000/api/get_result?job_id=<task_id>"
```

## Конфигурация

Секреты и адрес Redis читаются из окружения (см. `.env.example`): `SECRET_KEY`,
`DEBUG`, `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND`. Дефолты в `settings.py`
рассчитаны только на локальный запуск.
