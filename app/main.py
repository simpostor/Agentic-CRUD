from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.security import encrypt_key
from app.database import pool
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For production, replace "*" with your actual iPhone/Mac IP
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class VaultEntry(BaseModel):
    service_name: str
    api_key: str

@app.post("/vault/save")
async def save_credential(entry: VaultEntry):
    try:
        encrypted = encrypt_key(entry.api_key)
        with pool.acquire() as conn:
            with conn.cursor() as cursor:
                sql = """
                MERGE INTO vault_credentials t 
                USING (SELECT :1 as s, :2 as k FROM dual) s 
                ON (t.service_name = s.s) 
                WHEN MATCHED THEN UPDATE SET encrypted_api_key = s.k, updated_at = CURRENT_TIMESTAMP 
                WHEN NOT MATCHED THEN INSERT (service_name, encrypted_api_key) VALUES (s.s, s.k)
                """
                cursor.execute(sql, [entry.service_name.upper(), encrypted])
                conn.commit()
        return {"status": "Configured ✅"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)