# دليل نشر MikroTik AI Assistant - الجزء الأول: إعداد الخادم

هذا الدليل يفترض أن لديك خادمًا سحابيًا (Virtual Private Server - VPS) يعمل بنظام التشغيل **Ubuntu 22.04** أو أحدث.

## 1. الاتصال بالخادم وتحديث النظام

استخدم برنامج SSH (مثل PuTTY أو Terminal) للاتصال بالخادم:

```bash
ssh user@your_server_ip
```

بعد الاتصال، قم بتحديث قائمة الحزم وترقية النظام:

```bash
sudo apt update && sudo apt upgrade -y
```

## 2. تثبيت المتطلبات الأساسية

نحتاج إلى تثبيت Python، مدير الحزم `pip`، وبيئة افتراضية، بالإضافة إلى أدوات التطوير:

```bash
sudo apt install python3-pip python3-venv build-essential -y
```

## 3. إعداد بيئة المشروع

سنقوم بإنشاء مجلد للمشروع وإعداد البيئة الافتراضية داخله.

### الخطوة 3.1: إنشاء مجلد المشروع

```bash
mkdir mikrotik-ai-assistant
cd mikrotik-ai-assistant
```

### الخطوة 3.2: إعداد البيئة الافتراضية

```bash
python3 -m venv venv
source venv/bin/activate
```
(ستلاحظ ظهور `(venv)` قبل سطر الأوامر، مما يدل على تفعيل البيئة الافتراضية).

## 4. نقل ملفات المشروع

يجب عليك نقل جميع ملفات المشروع التي تم تطويرها (بما في ذلك `main.py`، `database.py`، `ai_model.py`، ومجلد `static`) إلى مجلد `mikrotik-ai-assistant` على الخادم.

يمكنك استخدام الأمر `scp` لنقل الملفات من جهازك المحلي إلى الخادم:

```bash
# من جهازك المحلي
scp -r /path/to/local/mikrotik_ai_assistant user@your_server_ip:~/mikrotik-ai-assistant/
```

## 5. تثبيت مكتبات Python

بعد نقل الملفات وتفعيل البيئة الافتراضية، قم بتثبيت جميع المكتبات المطلوبة:

```bash
pip install fastapi uvicorn python-multipart python-routeros pydantic sqlalchemy python-routeros-api
```

## 6. إعداد خادم التطبيق الدائم (Gunicorn)

لضمان تشغيل التطبيق بشكل دائم وموثوق، سنستخدم **Gunicorn** كخادم تطبيق و **Nginx** كخادم وكيل عكسي (Reverse Proxy).

### الخطوة 6.1: تثبيت Gunicorn

```bash
pip install gunicorn
```

### الخطوة 6.2: اختبار تشغيل التطبيق باستخدام Gunicorn

يمكنك اختبار تشغيل الواجهة الخلفية (Backend) على المنفذ 8000:

```bash
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```
(اضغط `Ctrl+C` لإيقاف الاختبار).

بهذا تكون قد أتممت إعداد الخادم والبيئة الافتراضية والمشروع. في الجزء التالي، سنقوم بإعداد Gunicorn كخدمة نظام (Systemd Service) لضمان تشغيله التلقائي والدائم.
