# Task Manager API

API для управления задачами с веб-интерфейсом и Telegram-ботом.

## 🚀 Быстрый запуск

### Через Docker (рекомендуется)

1. **Клонируйте репозиторий**
   ```bash
   git clone <repository-url>
   cd task_manager
   ```

2. **Создайте файл .env**
   ```bash
   cp .env.example .env
   ```
   Отредактируйте файл .env и укажите ваш BOT_TOKEN для Telegram-бота.

3. **Запустите проект**
   ```bash
   docker-compose up -d --build
   ```

4. **Откройте приложение**
   - Веб-интерфейс: http://localhost:8000
   - API документация: http://localhost:8000/docs

### Локальный запуск

1. **Установите зависимости**
   ```bash
   pip install -r requirements.txt
   ```

2. **Настройте базу данных**
   - Установите PostgreSQL
   - Создайте базу данных
   - Обновите DATABASE_URL в .env

3. **Запустите миграции**
   ```bash
   alembic upgrade head
   ```

4. **Запустите приложение**
   ```bash
   uvicorn app.main:app --reload
   ```

## 📁 Структура проекта

```
task_manager/
├── app/
│   ├── bot/                    # Telegram-бот
│   │   ├── handlers.py        # Обработчики команд бота
│   │   ├── keyboards.py       # Клавиатуры бота
│   │   ├── states.py          # Состояния FSM
│   │   └── __main__.py        # Точка входа бота
│   ├── crud.py                # CRUD операции
│   ├── database.py            # Настройки базы данных
│   ├── enums.py               # Перечисления
│   ├── main.py                # FastAPI приложение
│   ├── models.py              # Модели SQLAlchemy
│   └── schemas.py             # Схемы Pydantic
├── alembic/                   # Миграции базы данных
├── nginx/                     # Конфигурация Nginx
├── static/                    # Статические файлы
├── templates/                 # HTML шаблоны
├── docker-compose.yml         # Docker Compose конфигурация
├── Dockerfile.prod            # Production Dockerfile
├── requirements.txt           # Зависимости Python
└── .env.example              # Пример переменных окружения
```

## 🛠 Технологии

- **Backend**: FastAPI, SQLAlchemy 2.0, Pydantic
- **Database**: PostgreSQL 16
- **Bot**: Aiogram 3.x
- **Containerization**: Docker, Docker Compose
- **Web Server**: Gunicorn, Uvicorn (development)

## 📚 API Эндпоинты

### Задачи

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/tasks` | Получить список задач |
| POST | `/tasks` | Создать новую задачу |
| GET | `/tasks/{id}` | Получить задачу по ID |
| PUT | `/tasks/{id}` | Обновить задачу |
| PUT | `/tasks/{id}/complete` | Отметить задачу как выполненную |
| DELETE | `/tasks/{id}` | Удалить задачу |

### Параметры запросов

- `completed` - фильтр по статусу выполнения
- `priority` - фильтр по приоритету (low, medium, high)
- `skip` - количество пропускаемых записей
- `limit` - максимальное количество записей

## 🤖 Telegram Бот

Бот поддерживает следующие команды:

- `/start` - Главное меню
- `/tasks` - Список всех задач
- `/add` - Добавить новую задачу
- `/help` - Справка по командам

### Функционал бота:

- Просмотр задач с фильтрацией
- Создание новых задач
- Редактирование существующих задач
- Отметка задач как выполненных
- Удаление задач
- Навигация через inline-кнопки

## 🔧 Конфигурация

### Переменные окружения

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `DATABASE_URL` | Строка подключения к БД | - |
| `BOT_TOKEN` | Токен Telegram-бота | - |

### Настройки базы данных

Пул соединений настроен для оптимизации производительности:
- `pool_size`: 10 постоянных соединений
- `max_overflow`: 20 дополнительных соединений
- `pool_pre_ping`: проверка соединений перед использованием
- `pool_recycle`: пересоздание соединений каждые 5 минут

## 🚀 Deployment

### Production развертывание

1. **Подготовьте переменные окружения**
   ```bash
   cp .env.example .env
   # Отредактируйте .env
   ```

2. **Запустите в production режиме**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d --build
   ```

### Health Checks

Все сервисы настроены с health checks:
- **PostgreSQL**: проверка доступности БД
- **App**: проверка доступности API
- **Bot**: автоматический перезапуск при падении

## 📝 Миграции

### Создание новой миграции
```bash
alembic revision --autogenerate -m "Описание миграции"
```

### Применение миграций
```bash
alembic upgrade head
```

### Откат миграции
```bash
alembic downgrade -1
```

## 🧪 Тестирование

### Запуск тестов
```bash
pytest
```

### Проверка типов
```bash
mypy app/
```

## 📄 Лицензия

MIT License