from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.staticfiles import StaticFiles as StarletteStaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime
import json

# تأكد من وجود هذه الملفات: database.py و ai_model.py
from database import init_db, get_db, MikroTikConnection, SystemResource
from ai_model import analyze_log_message
import routeros_api

# تهيئة قاعدة البيانات
init_db()

app = FastAPI(title="MikroTik AI Assistant Backend")

# كود CORS
origins = [
    "https://mikroflowpro-ui.github.io", # نطاق الواجهة الأمامية المنشور
    "http://localhost",
    "http://localhost:8080",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# نموذج البيانات
class ConnectionData(BaseModel):
    name: str = None
    host: str
    port: int
    username: str
    password: str = None

# مسارات API
@app.get("/")
def read_root():
    return {"message": "MikroTik AI Assistant Backend is running."}

@app.post("/connections/")
def create_connection(data: ConnectionData, db: Session = Depends(get_db)):
    try:
        # حفظ بيانات الاتصال في قاعدة البيانات
        new_connection = MikroTikConnection(
            router_name=data.name, # التعديل الذي يحل مشكلة 'name' is an invalid keyword
            host=data.host,
            port=data.port,
            username=data.username,
            password=data.password
        )
        db.add(new_connection)
        db.commit()
        db.refresh(new_connection)
        
        return {"message": "Connection established and saved successfully.", "id": new_connection.id}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to connect or save: {str(e)}")

# خدمة الملفات الثابتة
app.mount("/", StaticFiles(directory="static", html=True), name="static")
