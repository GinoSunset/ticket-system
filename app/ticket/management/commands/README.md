README — add_itsm_ticket management command

Назначение

Команда `add_itsm_ticket` получает запись из ITSM по её `sys_id` и создаёт локальный `Ticket` в Django-приложении, используя существующие утилиты в `ticket.handlers_itsm`.

Расположение

`app/ticket/management/commands/add_itsm_ticket.py`

Пример запуска

В корне проекта (используется `app/manage.py`):

```fish
python3 app/manage.py add_itsm_ticket <sys_id>
```

Где `<sys_id>` — идентификатор записи в ITSM.

Что делает

- Формирует URL к ITSM: `get_url()` + `/sys_id`.
- Делает GET с хедером авторизации (`get_with_auth_header`).
- Обрабатывает JSON через `process_response`.
- В зависимости от формата ответа выбирает задачу (словарь или первый элемент списка).
- Вызывает `create_itsm_task(task)` — эта функция создаёт `Ticket` в базе.

Зависимости и переменные окружения

Код использует настройки Django из `settings.py`:
- `ITSM_BASE_URL`
- `ITSM_TASK_URL`
- `ITSM_USER`, `ITSM_PASSWORD`, `ITSM_USER_ID`
- `TICKET_CREATOR_USERNAME`

Тестирование

Файл тестов: `app/ticket/tests/test_add_itsm_ticket_command.py`

Тесты используют `monkeypatch` для замены:
- `get_with_auth_header`
- `process_response`
- `create_itsm_task`

Запуск теста:

```fish
pytest app/ticket/tests/test_add_itsm_ticket_command.py -q
```

Примечания и расширения

- Команда ожидает, что `create_itsm_task` корректно обработает все валидации (существующий SAP id и т.д.).
- Можно добавить флаги: `--force` для перезаписи существующих тикетов, `--timeout` для настройки сетевого запроса.
- Для интеграционных тестов требуется мок/фикстура внешнего HTTP и настройки тестовой БД.
