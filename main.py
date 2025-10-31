from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime
import routeros_api
import json

from database import init_db, get_db, MikroTikConnection, SystemResource, SystemLog
from ai_model import analyze_log_message

# تهيئة قاعدة البيانات عند بدء تشغيل التطبيق
init_db()

app = FastAPI(title="MikroTik AI Assistant Backend")

# إضافة دعم CORS للسماح للواجهة الأمامية بالاتصال
origins = [
    "*" # السماح بالوصول من أي مصدر لغرض الاختبار
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# خدمة الملفات الثابتة (Frontend)
app.mount("/static", StaticFiles(directory="static"), name="static")


# ----------------------------------------------------------------------
# نماذج Pydantic للتحقق من صحة البيانات (Schemas)
# ----------------------------------------------------------------------

class ConnectionBase(BaseModel):
    alias: str
    host: str
    port: int = 8728
    username: str
    password: str

class ConnectionCreate(ConnectionBase):
    pass

class Connection(ConnectionBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

class ResourceData(BaseModel):
    cpu_load: float
    free_memory_mb: float
    total_memory_mb: float
    uptime: str

# ----------------------------------------------------------------------
# الدوال المساعدة للاتصال بـ MikroTik
# ----------------------------------------------------------------------

def connect_to_mikrotik(host: str, port: int, user: str, password: str):
    """ينشئ اتصالاً بجهاز MikroTik ويقوم بإرجاع كائن API."""
    try:
        # يجب أن يكون الاتصال آمناً (SSL) في بيئة الإنتاج
        api = routeros_api.RouterOsApiPool(
            host, 
            username=user, 
            password=password, 
            port=port, 
            plaintext_login=False, # يجب أن يكون False في بيئة الإنتاج
            use_ssl=True # يجب تفعيل SSL في بيئة الإنتاج
        )
        return api.get_api()
    except routeros_api.exceptions.RouterOsApiError as e:
        raise HTTPException(status_code=400, detail=f"فشل الاتصال بـ MikroTik: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطأ غير متوقع أثناء الاتصال: {e}")

def fetch_system_resources(api):
    """يسحب بيانات موارد النظام من MikroTik."""
    try:
        resource = api.get_resource('/system/resource').get()[0]
        
        # تحويل البيانات إلى تنسيق مناسب
        cpu_load = float(resource.get('cpu-load', '0').replace('%', ''))
        total_memory_mb = float(resource.get('total-memory', '0').replace('MiB', ''))
        free_memory_mb = float(resource.get('free-memory', '0').replace('MiB', ''))
        uptime = resource.get('uptime', '0s')
        
        return ResourceData(
            cpu_load=cpu_load,
            free_memory_mb=free_memory_mb,
            total_memory_mb=total_memory_mb,
            uptime=uptime
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"فشل سحب موارد النظام: {e}")

# ----------------------------------------------------------------------
# واجهات برمجة التطبيقات (API Endpoints)
# ----------------------------------------------------------------------

@app.post("/connections/", response_model=Connection, tags=["Connections"])
def create_mikrotik_connection(connection: ConnectionCreate, db: Session = Depends(get_db)):
    """
    إنشاء اتصال جديد بجهاز MikroTik وحفظ بياناته في قاعدة البيانات.
    """
    # اختبار الاتصال قبل الحفظ
    try:
        api = connect_to_mikrotik(connection.host, connection.port, connection.username, connection.password)
        api.disconnect()
    except HTTPException as e:
        raise e
    
    db_connection = MikroTikConnection(**connection.dict())
    db.add(db_connection)
    db.commit()
    db.refresh(db_connection)
    return db_connection

@app.get("/connections/{connection_id}/resources", response_model=ResourceData, tags=["Data Fetching"])
def get_live_resources(connection_id: int, db: Session = Depends(get_db)):
    """
    سحب بيانات موارد النظام الحية (CPU, RAM, Uptime) من جهاز MikroTik محدد.
    """
    db_connection = db.query(MikroTikConnection).filter(MikroTikConnection.id == connection_id).first()
    if db_connection is None:
        raise HTTPException(status_code=404, detail="لم يتم العثور على اتصال MikroTik")

    # 1. الاتصال بجهاز MikroTik
    api = connect_to_mikrotik(db_connection.host, db_connection.port, db_connection.username, db_connection.password)
    
    # 2. سحب الموارد
    resources = fetch_system_resources(api)
    
    # 3. حفظ البيانات في قاعدة البيانات (للسجلات التاريخية والتحليل)
    db_resource = SystemResource(
        mikrotik_id=connection_id,
        cpu_load=resources.cpu_load,
        free_memory_mb=resources.free_memory_mb,
        total_memory_mb=resources.total_memory_mb,
        uptime=resources.uptime
    )
    db.add(db_resource)
    db.commit()
    
    api.disconnect()
    return resources

@app.get("/connections/{connection_id}/logs", tags=["Data Fetching"])
def get_live_logs(connection_id: int, db: Session = Depends(get_db)):
    """
    سحب سجلات النظام الحية من جهاز MikroTik محدد.
    """
    db_connection = db.query(MikroTikConnection).filter(MikroTikConnection.id == connection_id).first()
    if db_connection is None:
        raise HTTPException(status_code=404, detail="لم يتم العثور على اتصال MikroTik")

    # 1. الاتصال بجهاز MikroTik
    api = connect_to_mikrotik(db_connection.host, db_connection.port, db_connection.username, db_connection.password)
    
    # 2. سحب السجلات (آخر 100 سجل)
    try:
        logs = api.get_resource('/log').get()
    except Exception as e:
        api.disconnect()
        raise HTTPException(status_code=500, detail=f"فشل سحب السجلات: {e}")
        
    api.disconnect()
    
    # 3. حفظ السجلات في قاعدة البيانات (لتحليل الذكاء الاصطناعي)
    for log in logs:
        # يجب إضافة منطق للتحقق من عدم تكرار السجلات قبل الحفظ
        db_log = SystemLog(
            mikrotik_id=connection_id,
            timestamp=datetime.strptime(f"{log['time'].split()[0]}/{datetime.now().year} {log['time'].split()[1]}", "%b/%d/%Y %H:%M:%S"), # تبسيط التاريخ
            topics=log.get('topics', 'unknown'),
            message=log.get('message', 'no message')
        )
        db.add(db_log)
    db.commit()
    
    # 4. تحليل السجلات باستخدام الذكاء الاصطناعي
    analyzed_logs = []
    for log in logs:
        analysis = analyze_log_message(log.get('message', ''))
        analyzed_logs.append({
            "timestamp": log.get('time'),
            "topics": log.get('topics'),
            "message": log.get('message'),
            "analysis": analysis
        })
        
    return analyzed_logs

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "MikroTik AI Assistant Backend is running."}
