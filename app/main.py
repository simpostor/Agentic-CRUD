from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from fastapi.responses import StreamingResponse
from app.security import encrypt_key
from app.database import pool
from app.agent import MultiLLMOrchestrator 
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Models ---
class AuthRequest(BaseModel):
    username: str
    password: str

class VaultEntry(BaseModel):
    username: str
    service_name: str
    api_key: str

class ChatMessage(BaseModel):
    role: str
    text: str

class ChatRequest(BaseModel):
    username: str
    message: str
    history: Optional[List[ChatMessage]] = []

class Employee(BaseModel):
    name: str
    role: str
    department: str
    salary: float


# --- Routes ---

@app.post("/auth/login")
async def login(req: AuthRequest):
    try:
        with pool.acquire() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT password_hash FROM user_accounts WHERE username = :1", [req.username])
                row = cursor.fetchone()
                
                if not row:
                    # Auto-register new user
                    cursor.execute("INSERT INTO user_accounts (username, password_hash) VALUES (:1, :2)", 
                                 [req.username, req.password])
                    conn.commit()
                    return {"status": "success", "info": "Registered"}
                
                # Check password
                if row[0] == req.password:
                    return {"status": "success"}
                else:
                    # Explicit error for wrong password
                    raise HTTPException(status_code=401, detail="Incorrect password for this user.")
                
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Auth System Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Database Error")

@app.get("/user/check-keys/{username}")
async def check_keys(username: str):
    with pool.acquire() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT count(*) FROM vault_credentials WHERE username = :1", [username])
            count = cursor.fetchone()[0]
    return {"has_keys": count > 0}

@app.post("/vault/save")
async def save_credential(entry: VaultEntry):
    try:
        encrypted = encrypt_key(entry.api_key)
        with pool.acquire() as conn:
            with conn.cursor() as cursor:
                sql = """
                MERGE INTO vault_credentials t 
                USING (SELECT :1 as u, :2 as s, :3 as k FROM dual) s 
                ON (t.username = s.u AND t.service_name = s.s) 
                WHEN MATCHED THEN UPDATE SET encrypted_api_key = s.k, updated_at = CURRENT_TIMESTAMP 
                WHEN NOT MATCHED THEN INSERT (username, service_name, encrypted_api_key) VALUES (s.u, s.s, s.k)
                """
                cursor.execute(sql, [entry.username, entry.service_name.upper(), encrypted])
                conn.commit()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    try:
        orchestrator = MultiLLMOrchestrator(req.username)
        history_dicts = [m.model_dump() for m in req.history] if req.history else []
        
        # Call the standard non-streaming chat method
        status, response = await orchestrator.chat(req.message, history=history_dicts)
        
        return {"status": status, "reply": response}
    except Exception as e:
        print(f"Chat Error: {e}")
        return {"status": "error", "reply": f"System Error: {str(e)}"}
    
# --- Employee CRUD Endpoints ---

@app.get("/employees")
async def get_employees():
    with pool.acquire() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, name, role, department, salary FROM employees ORDER BY id DESC")
            rows = cursor.fetchall()
            return [{"id": r[0], "name": r[1], "role": r[2], "department": r[3], "salary": r[4]} for r in rows]

@app.post("/employees")
async def create_employee(emp: Employee):
    with pool.acquire() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO employees (name, role, department, salary) VALUES (:1, :2, :3, :4)",
                [emp.name, emp.role, emp.department, emp.salary]
            )
            conn.commit()
    return {"status": "Employee Created"}

@app.put("/employees/{emp_id}")
async def update_employee(emp_id: int, emp: Employee):
    with pool.acquire() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE employees SET name=:1, role=:2, department=:3, salary=:4 WHERE id=:5",
                [emp.name, emp.role, emp.department, emp.salary, emp_id]
            )
            conn.commit()
    return {"status": "Employee Updated"}

@app.delete("/employees/{emp_id}")
async def delete_employee(emp_id: int):
    with pool.acquire() as conn:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM employees WHERE id = :1", [emp_id])
            conn.commit()
    return {"status": "Employee Deleted"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)