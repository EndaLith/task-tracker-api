from fastapi import FastAPI,HTTPException,Depends
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import jwt,JWTError
from datetime import datetime,timedelta
import sqlite3


app = FastAPI()
pwd_context=CryptContext(schemes=["bcrypt"],deprecated="auto")
SECRET_KEY="this-is-a-highly-confidential-key-that-needs-to-be-changed"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=60
class Task(BaseModel):
    id: int
    title: str
    description: str
    completed: bool
class UserRegister(BaseModel):    
    username:str
    password:str

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
    conn.execute(
        """ CREATE TABLE IF NOT EXISTS users
        (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        hashed_password TEXT NOT NULL
        )
        """
    )
    try:
        conn.execute("ALTER TABLE tasks ADD COLUMN owner TEXT")
    except sqlite3.OperationalError:
        pass    
    conn.commit()
    conn.close()
init_db()
def create_access_token(username:str):
    expire=datetime.utcnow()+timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    data={"sub":username,"exp":expire}
    token=jwt.encode(data,SECRET_KEY,algorithm=ALGORITHM)
    return token
oauth2_scheme=OAuth2PasswordBearer(tokenUrl="login")
def get_current_user(token:str=Depends(oauth2_scheme)):
    try:
        payload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        username=payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401,detail="Invalid token")
        return username
    except JWTError:
        raise HTTPException(status_code=401,details="Invalid token")
@app.get("/")
def read_root():
    return {"message": "Hello, Task Tracker API is running!"}

@app.get("/tasks")
def get_tasks(current_user:str=Depends(get_current_user),completed:bool | None = None):
    conn = get_db_connection()
    if completed is None:
        rows = conn.execute("SELECT * FROM tasks WHERE owner=?",(current_user,)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM tasks WHERE owner=? AND completed=?",(current_user,completed)).fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.get("/tasks/{task_id}")
def get_task(task_id:int,current_user:str=Depends(get_current_user)):
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM tasks WHERE id=? AND owner=?", (task_id,current_user)).fetchone()
    conn.close()
    if row is None:
        raise HTTPException(status_code=404,detail="Task not found")
    return dict(row)

@app.post("/tasks")
def create_task(task: Task,current_user:str = Depends(get_current_user)):
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO tasks (id,title,description,completed,owner) VALUES (?,?,?,?,?)", (task.id, task.title, task.description, task.completed,current_user)
    )
    conn.commit()
    conn.close()
    return task

@app.put("/tasks/{task_id}")
def update_task(task_id: int, update_task: Task,current_user:str=Depends(get_current_user)):
    conn = get_db_connection()
    result = conn.execute(
        "UPDATE tasks SET title = ?, description=?, completed=? WHERE id=? AND owner=?", (update_task.title, update_task.description, update_task.completed, task_id,current_user)
    )
    conn.commit()
    conn.close()
    if result.rowcount == 0:
        raise HTTPException (status_code=404,detail="Task not found")
    return update_task

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int,current_user:str= Depends(get_current_user)):
    conn = get_db_connection()
    result = conn.execute("DELETE FROM tasks WHERE id=? AND owner=?", (task_id,current_user))
    conn.commit()
    conn.close()
    if result.rowcount == 0:
        raise HTTPException (status_code=404,detail="Task not found")
    return {"message": "Task deleted"}

@app.post("/register")
def register(user:UserRegister):
    conn=get_db_connection()
    hashed_password=pwd_context.hash(user.password)
    try:
        conn.execute(
            "INSERT INTO users (username,hashed_password) VALUES (?,?)",(user.username,hashed_password)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=400,detail="Username already exists")
    conn.close()
    return{"message":"User registered successfully"}    

@app.post("/login")
def login(form_data:OAuth2PasswordRequestForm=Depends()):
    conn=get_db_connection()
    row=conn.execute(
        "SELECT * FROM users WHERE username=?",(form_data.username,)
    ).fetchone()
    conn.close()
    if row is None:
        raise HTTPException(status_code=401,detail="Invalid username or password")
    if not pwd_context.verify(form_data.password,row["hashed_password"]):
        raise HTTPException(status_code=401,detail="Invalid username or password")
    token=create_access_token(form_data.username)
    return {"access_token":token,"token_type":"bearer"}