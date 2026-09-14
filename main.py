from fastapi import FastAPI,HTTPException
from pydantic import BaseModel
import sqlite3


app = FastAPI()

class Task(BaseModel):
    id: int
    title: str
    description: str
    completed: bool

def get_db_connection():
    conn = sqlite3.connect("tasks.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks(
            id int primary key,
            title text not null,
            description text,
            completed boolean not null
            )
        """
    )
    conn.commit()
    conn.close()
init_db()

@app.get("/")
def read_root():
    return {"message": "Hello, Task Tracker API is running!"}

@app.get("/tasks")
def get_tasks():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM tasks").fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
    conn.close()
    if row is None:
        raise HTTPException(status_code=404,detail="Task not found")
    return dict(row)

@app.post("/tasks")
def create_task(task: Task):
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO tasks (id,title,description,completed) VALUES (?,?,?,?)", (task.id, task.title, task.description, task.completed)
    )
    conn.commit()
    conn.close()
    return task

@app.put("/tasks/{task_id}")
def update_task(task_id: int, update_task: Task):
    conn = get_db_connection()
    result = conn.execute(
        "UPDATE tasks SET title = ?, description=?, completed=? WHERE id=?", (update_task.title, update_task.description, update_task.completed, task_id)
    )
    conn.commit()
    conn.close()
    if result.rowcount == 0:
        raise HTTPException (status_code=404,detail="Task not found")
    return update_task

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    conn = get_db_connection()
    result = conn.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conn.commit()
    conn.close()
    if result.rowcount == 0:
        raise HTTPException (status_code=404,detail="Task not found")
    return {"message": "Task deleted"}