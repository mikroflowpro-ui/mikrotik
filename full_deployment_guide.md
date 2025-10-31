# الدليل الشامل لنشر MikroTik AI Assistant على خادم إنتاج

هذا الدليل يجمع الخطوات اللازمة لنشر مشروعك (المبني على Python/FastAPI) بشكل دائم وآمن على خادم سحابي (VPS) يعمل بنظام Ubuntu.

## الجزء الأول: إعداد الخادم والبيئة

هذا الدليل يفترض أن لديك خادمًا سحابيًا (VPS) يعمل بنظام التشغيل **Ubuntu 22.04** أو أحدث.

### 1. الاتصال بالخادم وتحديث النظام

```bash
ssh user@your_server_ip
sudo apt update && sudo apt upgrade -y
```

### 2. تثبيت المتطلبات الأساسية

نحتاج إلى تثبيت Python، مدير الحزم `pip`، وبيئة افتراضية، بالإضافة إلى أدوات التطوير:

```bash
sudo apt install python3-pip python3-venv build-essential nginx -y
```

### 3. إعداد بيئة المشروع ونقل الملفات

```bash
mkdir mikrotik-ai-assistant
cd mikrotik-ai-assistant
python3 -m venv venv
source venv/bin/activate
```

**نقل الملفات:** استخدم الأمر `scp` لنقل جميع ملفات المشروع (بما في ذلك `main.py`، `database.py`، `ai_model.py`، ومجلد `static`) من جهازك المحلي إلى مجلد `mikrotik-ai-assistant` على الخادم.

### 4. تثبيت مكتبات Python

```bash
pip install fastapi uvicorn python-multipart python-routeros pydantic sqlalchemy python-routeros-api gunicorn
```

## الجزء الثاني: نشر التطبيق (Gunicorn و Nginx)

سنقوم بإعداد Gunicorn كخدمة نظام (Systemd) واستخدام Nginx كخادم وكيل عكسي.

### 1. إعداد خدمة Gunicorn (Systemd)

قم بإنشاء الملف التالي:

```bash
sudo nano /etc/systemd/system/mikrotik_ai.service
```

وأضف المحتوى التالي، مع استبدال `your_username` باسم المستخدم الخاص بك:

```ini
[Unit]
Description=Gunicorn instance to serve MikroTik AI Assistant
After=network.target

[Service]
User=your_username
Group=www-data
WorkingDirectory=/home/your_username/mikrotik-ai-assistant
ExecStart=/home/your_username/mikrotik-ai-assistant/venv/bin/gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind unix:/run/mikrotik_ai.sock

[Install]
WantedBy=multi-user.target
```

**تفعيل وتشغيل الخدمة:**

```bash
sudo systemctl daemon-reload
sudo systemctl start mikrotik_ai
sudo systemctl enable mikrotik_ai
sudo systemctl status mikrotik_ai
```

### 2. إعداد خادم Nginx كوكيل عكسي

قم بإنشاء ملف إعداد جديد لموقعك:

```bash
sudo nano /etc/nginx/sites-available/mikrotik_ai
```

وأضف المحتوى التالي، مع استبدال `your_domain.com` بنطاقك الفعلي:

```nginx
server {
    listen 80;
    server_name your_domain.com www.your_domain.com;

    location / {
        # توجيه الطلبات إلى Gunicorn عبر ملف السوكيت
        proxy_pass http://unix:/run/mikrotik_ai.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # خدمة الملفات الثابتة مباشرة من Nginx (أسرع)
    location /static/ {
        alias /home/your_username/mikrotik-ai-assistant/static/;
    }
}
```

**تفعيل الإعداد وإعادة تشغيل Nginx:**

```bash
sudo ln -s /etc/nginx/sites-available/mikrotik_ai /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## الجزء الثالث: تأمين التطبيق (SSL/TLS)

سنستخدم Certbot وشهادات Let's Encrypt المجانية لتأمين الاتصال (HTTPS).

### 1. تثبيت Certbot

```bash
sudo apt install certbot python3-certbot-nginx -y
```

### 2. الحصول على شهادة SSL

```bash
sudo certbot --nginx -d your_domain.com -d www.your_domain.com
```
(اتبع التعليمات، واختر إعادة توجيه (Redirect) لجميع طلبات HTTP إلى HTTPS).

### 3. إعداد جدار الحماية (Firewall)

```bash
sudo apt install ufw -y
sudo ufw enable
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full' # يسمح بـ 80 و 443
sudo ufw status
```

باتباع هذا الدليل، سيكون موقع **MikroTik AI Assistant** الخاص بك منشورًا بشكل دائم وآمن، وجاهزًا للاتصال بأجهزة MikroTik عبر عنوان IP حقيقي.
