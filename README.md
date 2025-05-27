# python-advanced-intro-4

## Проект по разработке микросервиса и автоматизации API-тестирования
## Описание проект
В рамках проекта разарботан микросервис на FastAPI, представлюящий RESTful API для управления пользовательскими данными. Микросервис включает:
- Создание, чтение, обновление и удаление пользовательских данных (CRUD)
- Валидацию входных данных с использованием Pydantic
- Логирование и обработку ошибок
- Автоматическое документирование через Swagger UI

### Шаги
1. Склонировать проект
   ```bash
   git clone https://github.com/avdarya/python-advanced-intro-4.git
2. Установить зависимости
    ```bash
    pip install -r requirements.txt
3. Запустить микросервис:
    ```bash
    python main.py
4. Запустить тесты:
    ```bash
   pytest

### Технологический стек:
- **Backend:** FastAPI, Uvicorn
- **Тестирование:** Pytest, Requests
- **Валидация:** Pydantic, JSON Schema
- **Документация:** Swagger UI (доступна по /docs)

### Структура проекта
- main.py - реализация микросервиса
- requirements.txt - зависимости проекта
- single_user.json - JSON Schema для ответа API
- single_user_schema.py - схема ответа в формате Python
- test_my_reqres.py - тесты для локального микросервиса
- test_reqres_single_user.py - тесты для внешнего API (reqres.in)

### Настройки окружения

### Тестовые данные
Тестовые данные передаются через параметризованные тесты в файлах:
- test_my_reqres.py (для локального микросервиса)
- test_reqres_single_user.py (для reqres.in)

### Установка зависимостей
- Одной командой:
    ```bash
    pip install -r requirements.txt
- Или по отдельности:
    ```bash
    pip install pytest requests fastapi uvicorn pydantic jsonschema

### Запуск тестов
- Все тесты:
    ```bash
    pytest
- Только тесты микросервиса:
    ```bash
    pytest test_my_reqres.py
- Только тесты reqres.in:
    ```bash
    pytest test_reqres_single_user.py

### Особенности реализации
- Валидация данных на уровне моделей Pydantic
- Подробные сообщения об ошибках
- Полное покрытие CRUD-операций тестами
- Поддержка JSON Schema для валидации ответов