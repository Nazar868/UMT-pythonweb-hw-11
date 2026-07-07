# UMT-pythonweb-hw-11 — Contacts REST API

REST API для зберігання та управління контактами з аутентифікацією,
авторизацією через JWT, верифікацією email, обмеженням запитів,
CORS та завантаженням аватара через Cloudinary.

## Функціонал

- Реєстрація (`POST /api/auth/register`) — 201 Created, 409 Conflict якщо email зайнятий, пароль хешується (bcrypt).
- Логін (`POST /api/auth/login`) — приймає `username` (email) і `password` у формі, повертає `access_token`. 401 при неправильних даних.
- Усі захищені маршрути очікують заголовок:
  ```
  Authorization: Bearer <access_token>
  ```
- Контакти прив'язані до `owner_id` — кожен користувач бачить і редагує лише свої контакти.
- Верифікація email: після реєстрації надсилається лист із посиланням `GET /api/auth/confirmed_email/{token}`. Без підтвердження логін неможливий.
- `GET /api/users/me` обмежено до 5 запитів/хвилину з однієї IP.
- CORS увімкнено для всіх джерел.
- `PATCH /api/users/avatar` — завантаження аватара у Cloudinary.

## Запуск

1. Скопіюйте `.env.example` у `.env` та заповніть реальними значеннями (секрети, дані пошти, дані Cloudinary).
2. Запустіть:
   ```bash
   docker compose up --build
   ```
3. Swagger-документація: http://localhost:8000/docs

## Структура проєкту

```
main.py
src/
  conf/config.py        # конфігурація з .env
  database/
    db.py                # engine, SessionLocal, get_db
    models.py             # User, Contact
  schemas/                # Pydantic-схеми
  repository/              # доступ до БД (users, contacts)
  routes/                  # auth, users, contacts
  services/
    auth.py                # хешування паролів, JWT
    email.py                # відправка листа підтвердження
    avatar.py                # Cloudinary
    limiter.py                # slowapi rate limiter
```
