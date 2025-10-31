from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.staticfiles import StaticFiles as StarletteStaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime
import json

# استيراد المكتبات الخاصة بك
from database import init_db, get_db, MikroTikConnection, SystemResource
from ai_model import analyze_log_message
import routeros_api # تأكد من استيراد هذه المكتبة إذا كنت تستخدمها

# تهيئة قاعدة البيانات عند بدء تشغيل التطبيق
init_db()

app = FastAPI(title="MikroTik AI Assistant Backend")

# *****************************************************************
# ** كود CORS: السماح بالاتصال من نطاق GitHub Pages **
# *****************************************************************
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
    allow_methods=["*"], # السماح بجميع الطرق (GET, POST, PUT, DELETE)
    allow_headers=["*"], # السماح بجميع الرؤوس
)
# *****************************************************************

# *****************************************************************
# ** نموذج البيانات (Pydantic) **
# *****************************************************************
class ConnectionData(BaseModel):
    name: str = None
    host: str
    port: int
    username: str
    password: str = None

# *****************************************************************
# ** مسارات API **
# *****************************************************************

@app.get("/")
def read_root():
    return {"message": "MikroTik AI Assistant Backend is running."}

@app.post("/connections/")
def create_connection(data: ConnectionData, db: Session = Depends(get_db)):
    try:
        # 1. محاولة الاتصال بالراوتر (هذا الجزء يعتمد على مكتبة routeros_api الخاصة بك)
        # مثال:
        # client = routeros_api.RouterOsApiPool(
        #     data.host,
        #     username=data.username,
        #     password=data.password,
        #     port=data.port,
        #     plaintext_login=True
        # )
        # api = client.get_api()
        # api.get_resource('/system/resource').get()
        
        # 2. حفظ بيانات الاتصال في قاعدة البيانات (لغرض المحاكاة أو الاستخدام المستقبلي)
        new_connection = MikroTikConnection(
            router_name=data.name, # <--- التعديل الصحيح: تغيير 'name' إلى 'router_name'
            host=data.host,
            port=data.port,
            username=data.username,
            password=data.password # يفضل تشفير كلمة المرور في تطبيق حقيقي
        )
        db.add(new_connection)
        db.commit()
        db.refresh(new_connection)
        
        # 3. إرجاع رسالة نجاح
        return {"message": "Connection established and saved successfully.", "id": new_connection.id}
    
    except Exception as e:
        # 4. إرجاع خطأ في حالة فشل الاتصال أو الحفظ
        raise HTTPException(status_code=400, detail=f"Failed to connect or save: {str(e)}")

# *****************************************************************
# ** خدمة الملفات الثابتة (Frontend) **
# *****************************************************************
# تأكد من أن هذا الجزء موجود في نهاية الملف
app.mount("/", StaticFiles(directory="static", html=True), name="static")
