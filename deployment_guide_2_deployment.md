# دليل نشر MikroTik AI Assistant - الجزء الثاني: نشر التطبيق

بعد إعداد الخادم وتثبيت المتطلبات الأساسية في الجزء الأول، سنقوم الآن بإعداد Gunicorn كخدمة نظام (Systemd) واستخدام Nginx كخادم وكيل عكسي (Reverse Proxy) لضمان التشغيل الدائم والموثوق.

## 1. إعداد خدمة Gunicorn (Systemd)

سنقوم بإنشاء ملف خدمة Systemd لتشغيل Gunicorn تلقائيًا عند بدء تشغيل الخادم.

### الخطوة 1.1: إنشاء ملف الخدمة

قم بإنشاء الملف التالي:

```bash
sudo nano /etc/systemd/system/mikrotik_ai.service
```

وأضف المحتوى التالي، مع التأكد من استبدال `your_username` باسم المستخدم الخاص بك على الخادم:

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

### الخطوة 1.2: تفعيل وتشغيل الخدمة

```bash
sudo systemctl daemon-reload
sudo systemctl start mikrotik_ai
sudo systemctl enable mikrotik_ai
```

### الخطوة 1.3: التحقق من حالة الخدمة

تأكد من أن الخدمة تعمل بشكل صحيح:

```bash
sudo systemctl status mikrotik_ai
```

## 2. إعداد خادم Nginx كوكيل عكسي (Reverse Proxy)

سنستخدم Nginx لتوجيه طلبات الويب من المنفذ 80/443 إلى Gunicorn الذي يعمل على منفذ داخلي (عبر ملف السوكيت).

### الخطوة 2.1: تثبيت Nginx

```bash
sudo apt install nginx -y
```

### الخطوة 2.2: إنشاء ملف إعداد Nginx

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

### الخطوة 2.3: تفعيل الإعداد وإعادة تشغيل Nginx

قم بإنشاء رابط رمزي لملف الإعداد في مجلد `sites-enabled`:

```bash
sudo ln -s /etc/nginx/sites-available/mikrotik_ai /etc/nginx/sites-enabled/
sudo nginx -t # اختبار الإعدادات
sudo systemctl restart nginx
```

بهذا، يكون تطبيقك يعمل بشكل دائم عبر Gunicorn، ويتم توجيه طلبات الويب إليه عبر Nginx. في الجزء التالي، سنتناول تأمين الاتصال باستخدام شهادة SSL/TLS.
