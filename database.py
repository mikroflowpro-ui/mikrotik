from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# استخدام SQLite كقاعدة بيانات مؤقتة
SQLALCHEMY_DATABASE_URL = "sqlite:///./mikrotik_ai.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# ----------------------------------------------------------------------
# نماذج قاعدة البيانات (Database Models)
# ----------------------------------------------------------------------

class MikroTikConnection(Base):
    """نموذج لتخزين بيانات اتصال جهاز MikroTik"""
    __tablename__ = "mikrotik_connections"

    id = Column(Integer, primary_key=True, index=True)
    alias = Column(String, index=True) # اسم مستعار للراوتر (مثل: راوتر الفرع الرئيسي)
    host = Column(String, unique=True, index=True)
    port = Column(Integer, default=8728)
    username = Column(String)
    password = Column(String) # في التطبيق الحقيقي يجب تشفير هذا الحقل
    created_at = Column(DateTime, default=datetime.utcnow)

class SystemResource(Base):
    """نموذج لتخزين بيانات موارد النظام (CPU, RAM, Uptime)"""
    __tablename__ = "system_resources"

    id = Column(Integer, primary_key=True, index=True)
    mikrotik_id = Column(Integer, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    cpu_load = Column(Float) # نسبة استخدام المعالج
    free_memory_mb = Column(Float)
    total_memory_mb = Column(Float)
    uptime = Column(String) # وقت التشغيل
    
class SystemLog(Base):
    """نموذج لتخزين سجلات النظام (Logs) لتحليل الذكاء الاصطناعي"""
    __tablename__ = "system_logs"

    id = Column(Integer, primary_key=True, index=True)
    mikrotik_id = Column(Integer, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    topics = Column(String) # مواضيع السجل (مثل: system, error, wireless)
    message = Column(Text) # نص رسالة السجل
    
# دالة لإنشاء الجداول في قاعدة البيانات
def init_db():
    Base.metadata.create_all(bind=engine)

# دالة للحصول على جلسة قاعدة البيانات
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
