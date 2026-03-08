# Task Manager API!!!!!!!!!!!!!!!!?
REST API для управления задачами.
Проект реализован на FastAPI + SQLAlchemy + PostgreSQL.
## 🚀 Стек технологий
- Python 3.11+
- FastAPI
- SQLAlchemy
- PostgreSQL
- Uvicorn
---
## 📦 Возможности
- Создание задачи
- Получение списка задач
- Фильтрация по статусу и приоритету
- Обновление задачи
- Отметка задачи как выполненной
- Удаление задачи
- Обработка ошибок (404)
- Автоматическая документация Swagger
---
## ⚙ Установка и запуск
1️⃣ Клонировать репозиторий
git clone https://github.com/your_username/task-manager-api.git
cd task-manager-api
2️⃣ Создать виртуальное окружение
Windows:
python -m venv venv
venv\Scripts\activate
Linux / macOS:
python3 -m venv venv
source venv/bin/activate
3️⃣ Установить зависимости
pip install -r requirements.txt
4️⃣ Настроить подключение к базе данных
В файле database.py указать строку подключения:
DATABASE_URL = "postgresql://user:password@localhost:5432/tasks_db"
Убедиться, что база данных создана.
5️⃣ Запустить сервер
uvicorn main:app --reload
Сервер будет доступен по адресу:
http://127.0.0.1:8000
Swagger документация:
http://127.0.0.1:8000/docs
📌 Доступные endpoints
GET /tasks
Получить список задач.
Query параметры:
completed: true / false
priority: low / medium / high
POST /tasks
Создать новую задачу.
Пример JSON:
{
  "title": "Buy milk",
  "deadline": "2026-03-05",
  "priority": "high"
}
PUT /tasks/{task_id}
Обновить задачу (частично).
PUT /tasks/{task_id}/complete
Отметить задачу как выполненную.
DELETE /tasks/{task_id}
Удалить задачу.
Если задача не найдена — возвращается:
{
  "detail": "Task not found"
}
📊 Архитектура проекта
.
├── main.py        # endpoints
├── models.py      # SQLAlchemy модели
├── schemas.py     # Pydantic схемы
├── crud.py        # бизнес-логика
├── database.py    # подключение к БД
└── README.md
📚 Статус проекта
Учебный backend-проект для отработки:
REST архитектуры
Dependency Injection
ORM
Валидации данных
Обработки ошибок