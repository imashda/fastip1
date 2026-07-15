# FastIP — Task Management API

REST API для управления задачами с JWT авторизацией, ролевой системой и канбан-доской.

## Стек

- **FastAPI** — веб-фреймворк
- **SQLAlchemy** (async) + **aiosqlite** — работа с БД
- **Alembic** — миграции
- **Pydantic v2** — валидация данных
- **bcrypt** — хэширование паролей
- **python-jose** — JWT токены
- **pytest** + **pytest-asyncio** — тесты

## Структура проекта

```
├── app/
│   ├── __init__.py          # FastAPI app, middleware, lifespan
│   ├── auth.py              # JWT: создание и проверка токенов
│   ├── config.py            # Настройки из .env
│   ├── database.py          # Подключение к БД, get_session
│   ├── dependencies.py      # get_current_user, get_admin_user
│   ├── logging_config.py    # Логирование в консоль и файл
│   ├── models/
│   │   ├── user.py          # SQLAlchemy модель User
│   │   └── task.py          # SQLAlchemy модель Task
│   ├── repositories/
│   │   ├── user_repository.py   # CRUD пользователей
│   │   └── task_repository.py   # CRUD задач
│   ├── routers/
│   │   ├── auth.py          # POST /auth/register, /auth/login
│   │   ├── users.py         # GET/PUT/DELETE /users
│   │   ├── admin.py         # /admin/users (только для админа)
│   │   └── tasks.py         # CRUD /tasks
│   └── schemas/
│       ├── user.py          # Pydantic схемы пользователя
│       └── task.py          # Pydantic схемы задачи
├── migrations/              # Alembic миграции
├── tests/
│   ├── conftest.py          # Фикстуры pytest
│   ├── test_auth.py         # Тесты авторизации
│   └── test_tasks.py        # Тесты задач
├── .env                     # Переменные окружения (не в git)
├── .gitignore
├── alembic.ini
├── main.py                  # Точка входа
├── pytest.ini
└── requirements.txt
```

## Установка и запуск

**1. Клонируй репозиторий**
```bash
git clone https://github.com/imashda/fastip1
cd fastip
```

**2. Создай виртуальное окружение**
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux/Mac
```

**3. Установи зависимости**
```bash
pip install -r requirements.txt
```

**4. Создай `.env` файл**
```env
SECRET_KEY=your-super-secret-key-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=sqlite+aiosqlite:///./testik.sqlite
```

**5. Примени миграции**
```bash
alembic upgrade head
```

**6. Запусти сервер**
```bash
python main.py
```

Сервер запустится на `http://localhost:8000`

Swagger документация: `http://localhost:8000/docs`

## API

### Auth
| Метод | URL | Описание |
|-------|-----|----------|
| POST | `/auth/register` | Регистрация |
| POST | `/auth/login` | Вход, получение JWT токена |

### Users
| Метод | URL | Описание | Доступ |
|-------|-----|----------|--------|
| GET | `/users/me` | Свой профиль | Авторизован |
| GET | `/users/{id}` | Пользователь по ID | Себя или админ |
| PUT | `/users/{id}` | Обновить данные | Себя или админ |
| DELETE | `/users/{id}` | Удалить | Себя или админ |

### Tasks
| Метод | URL | Описание | Доступ |
|-------|-----|----------|--------|
| POST | `/tasks` | Создать задачу | Авторизован |
| GET | `/tasks` | Мои задачи | Авторизован |
| GET | `/tasks/{id}` | Задача по ID | Владелец или админ |
| PATCH | `/tasks/{id}` | Обновить задачу | Владелец или админ |
| PATCH | `/tasks/{id}/status` | Изменить статус | Владелец или админ |
| DELETE | `/tasks/{id}` | Удалить задачу | Владелец или админ |
| GET | `/tasks/admin/all` | Все задачи | Только админ |

### Admin
| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/admin/users` | Все пользователи |
| DELETE | `/admin/users/{id}` | Удалить пользователя |
| PUT | `/admin/users/{id}/make-admin` | Назначить админа |

## Статусы задач

```
backlog → todo → in_progress → review → done
```

## Приоритеты задач

- `low` — низкий
- `medium` — средний
- `high` — высокий
- `critical` — критический

## Тесты

```bash
pytest tests/ -v
```

## Первый администратор

После регистрации первого пользователя назначь его админом вручную:

```bash
python make_admin.py
```

Или через SQLite напрямую:
```sql
UPDATE users SET is_admin = 1 WHERE username = 'твой_username';
```

## Логирование

Логи пишутся одновременно в консоль и в файл `app.log`:

```
2026-07-16 00:30:23 | INFO | app | Успешный вход: username=admin, id=1
2026-07-16 00:30:23 | INFO | app | POST /auth/login -> 200 (301.86 ms)
```
