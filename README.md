# Task Tracker API

A simple REST API for managing personal tasks, built with FastAPI and SQLite. Each user registers an account and can only view, update, or delete their own tasks. Authentication is handled with JWT tokens.

## Features

- User registration and login with hashed passwords (bcrypt)
- JWT-based authentication
- Full CRUD operations for tasks (create, read, update, delete)
- Tasks are scoped per user — one user cannot access another user's tasks
- SQLite database for persistent storage
- Interactive API documentation via Swagger UI

## Tech Stack

- Python
- FastAPI
- SQLite
- Pydantic (data validation)
- python-jose (JWT tokens)
- passlib + bcrypt (password hashing)

## Setup

1. Clone the repository:
```git clone https://github.com/EndaLith/task-tracker-api.git
```cd task-tracker-api
2. Create and activate a virtual environment:
```python -m venv venv
```venv\Scripts\activate 
```(for windows)
3. Install dependencies:
```pip install fastapi uvicorn "python-jose[cryptography]" "passlib[bcrypt]" python-multipart
4. Run the server:
```uvicorn main:app --reload
5. Open the interactive API docs in your browser:
```http://127.0.0.1:8000/docs

## Usage

1. Register a new user via `POST /register`.
2. Log in via `POST /login` to receive a JWT access token.
3. Click "Authorize" in the Swagger UI and enter your credentials to authenticate.
4. Use the `/tasks` endpoints to create, view, update, and delete your tasks.

## Endpoints

| Method | Endpoint          | Description                  | Auth required |
|--------|-------------------|-------------------------------|----------------|
| POST   | /register         | Create a new user account     | No             |
| POST   | /login            | Log in and receive a token    | No             |
| GET    | /tasks            | List all of your tasks        | Yes            |
| GET    | /tasks/{id}       | Get a single task             | Yes            |
| POST   | /tasks            | Create a new task             | Yes            |
| PUT    | /tasks/{id}       | Update an existing task       | Yes            |
| DELETE | /tasks/{id}       | Delete a task                 | Yes            |