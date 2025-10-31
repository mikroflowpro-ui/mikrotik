# دليل إعداد MikroTik للاتصال الآمن بـ MikroTik AI Assistant

لضمان عمل التطبيق بشكل صحيح وآمن مع جهاز MikroTik الخاص بك عبر عنوان IP حقيقي (Real IP)، يجب عليك اتباع الخطوات التالية لإعداد الراوتر:

## 1. تأمين الاتصال (الأهم)

يجب استخدام الاتصال المشفر (SSL/TLS) عبر منفذ API الآمن (8729) لحماية بيانات الاعتماد الخاصة بك.

### الخطوة 1: تفعيل شهادة SSL/TLS على MikroTik

1.  **الحصول على شهادة:** يفضل استخدام شهادة SSL/TLS صالحة (مثل Let's Encrypt) لجهاز MikroTik الخاص بك.
2.  **استيراد الشهادة:** قم باستيراد الشهادة والمفتاح الخاص إلى قائمة الشهادات في MikroTik (عبر WinBox: `System -> Certificates`).

### الخطوة 2: تفعيل خدمة API-SSL

1.  اذهب إلى `IP -> Services` في WinBox أو استخدم الأمر التالي:
    ```bash
    /ip service set api-ssl port=8729 certificate=اسم_الشهادة_الخاصة_بك disabled=no
    ```
2.  **تأكد من تعطيل API غير المشفر (Port 8728)** لزيادة الأمان:
    ```bash
    /ip service set api disabled=yes
    ```

## 2. إعداد المستخدم المخصص (الأمان)

لأسباب أمنية، يجب إنشاء مستخدم جديد بصلاحيات محدودة خصيصًا للتطبيق.

### الخطوة 1: إنشاء مجموعة صلاحيات مخصصة

قم بإنشاء مجموعة صلاحيات تسمح فقط بالقراءة والاختبار، وليس التعديل أو الكتابة:

```bash
/user group add name=ai-assistant-group policy=read,test,sniff
```

### الخطوة 2: إنشاء المستخدم

قم بإنشاء مستخدم جديد وقم بتعيينه للمجموعة التي أنشأتها:

```bash
/user add name=ai-assistant password=YourStrongPassword group=ai-assistant-group
```

**ملاحظة:** استخدم كلمة مرور قوية جدًا.

## 3. إعداد الجدار الناري (Firewall)

للسماح للتطبيق بالوصول إلى الراوتر عبر الإنترنت، يجب فتح منفذ API-SSL (8729) على الجدار الناري.

### الخطوة 1: إضافة قاعدة NAT (إذا كنت تستخدم NAT)

إذا كان جهاز MikroTik الخاص بك خلف راوتر آخر، يجب عمل Port Forwarding للمنفذ 8729 إلى عنوان IP الداخلي لجهاز MikroTik.

### الخطوة 2: إضافة قاعدة Filter

للسماح بالاتصال الوارد على المنفذ 8729:

```bash
/ip firewall filter add chain=input protocol=tcp dst-port=8729 action=accept comment="Allow AI Assistant API-SSL"
```

**نصيحة أمنية متقدمة:** إذا كان لديك عنوان IP ثابت للخادم الذي سيستضيف التطبيق، يمكنك تحديد مصدر الاتصال لزيادة الأمان:

```bash
/ip firewall filter add chain=input protocol=tcp src-address=IP_خادم_التطبيق dst-port=8729 action=accept comment="Allow AI Assistant from Server IP"
```

باتباع هذه الخطوات، سيكون جهاز MikroTik الخاص بك جاهزًا للاتصال الآمن بالتطبيق عبر عنوان IP الحقيقي.
