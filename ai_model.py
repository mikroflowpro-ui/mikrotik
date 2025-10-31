from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
import joblib
import os

# ----------------------------------------------------------------------
# بيانات تدريبية مبسطة (يجب توسيعها ببيانات حقيقية)
# ----------------------------------------------------------------------
# المشاكل المصنفة:
# 1: انقطاع الاتصال (Connection Loss)
# 2: ارتفاع استهلاك الموارد (High Resource Usage)
# 3: مشكلة في الواي فاي (Wireless Issue)
# 4: مشكلة أمنية (Security Issue)
# 5: مشكلة في DHCP (DHCP Issue)

TRAINING_DATA = [
    ("router rebooted", 1),
    ("link down", 1),
    ("ether1 link is down", 1),
    ("critical: out of memory", 2),
    ("cpu load is high", 2),
    ("cpu usage 95%", 2),
    ("client disconnected, reason: 4-way handshake timeout", 3),
    ("disconnected, signal strength too low", 3),
    ("login failure for user admin", 4),
    ("port scan detected", 4),
    ("dhcp-client on ether1 got IP", 5),
    ("dhcp-server assigned 192.168.1.100", 5),
    ("system,info: router started", 1), # بداية التشغيل بعد انقطاع
]

MODEL_PATH = "mikrotik_log_classifier.joblib"

def train_ai_model():
    """
    تدريب نموذج تصنيف بسيط باستخدام الانحدار اللوجستي (Logistic Regression)
    لتصنيف رسائل سجلات MikroTik.
    """
    print("بدء تدريب نموذج الذكاء الاصطناعي الأولي...")
    
    # فصل البيانات إلى رسائل (X) وتصنيفات (y)
    X = [item[0] for item in TRAINING_DATA]
    y = [item[1] for item in TRAINING_DATA]
    
    # إنشاء خط أنابيب (Pipeline) يجمع بين استخلاص الميزات والنموذج
    model = Pipeline([
        ('tfidf', TfidfVectorizer()),
        ('clf', LogisticRegression(max_iter=1000)),
    ])
    
    # تدريب النموذج
    model.fit(X, y)
    
    # حفظ النموذج المدرب
    joblib.dump(model, MODEL_PATH)
    print(f"تم تدريب وحفظ النموذج بنجاح في: {MODEL_PATH}")
    return model

def load_ai_model():
    """تحميل النموذج المدرب، أو تدريبه إذا لم يكن موجودًا."""
    if os.path.exists(MODEL_PATH):
        print(f"تحميل النموذج من: {MODEL_PATH}")
        return joblib.load(MODEL_PATH)
    else:
        print("لم يتم العثور على نموذج، بدء التدريب...")
        return train_ai_model()

# تحميل النموذج عند بدء تشغيل التطبيق
AI_CLASSIFIER = load_ai_model()

# ----------------------------------------------------------------------
# دالة التحليل الرئيسية
# ----------------------------------------------------------------------

def analyze_log_message(message: str) -> dict:
    """
    تحليل رسالة سجل وتقديم تصنيف وحل مقترح.
    """
    # 1. التصنيف باستخدام نموذج التعلم الآلي
    prediction = AI_CLASSIFIER.predict([message])[0]
    
    # 2. تحديد الحل المقترح بناءً على التصنيف
    if prediction == 1:
        category = "انقطاع الاتصال (Connection Loss)"
        solution = "تحقق من حالة الكابلات والمودم الخارجي. إذا استمر الانقطاع، قم بإعادة تشغيل الراوتر والمودم."
    elif prediction == 2:
        category = "ارتفاع استهلاك الموارد (High Resource Usage)"
        solution = "تحقق من العمليات النشطة في قائمة 'System/Resources/Processes'. قد تحتاج إلى تحديث نظام التشغيل أو تقليل عدد قواعد الجدار الناري."
    elif prediction == 3:
        category = "مشكلة في الواي فاي (Wireless Issue)"
        solution = "تحقق من قوة الإشارة (Signal Strength) للعميل. قد تحتاج إلى تغيير قناة الواي فاي (Channel) أو تركيب مقوي إشارة."
    elif prediction == 4:
        category = "مشكلة أمنية (Security Issue)"
        solution = "قم بتغيير كلمة مرور المستخدم 'admin' فورًا إلى كلمة قوية. تحقق من قواعد الجدار الناري لمنع محاولات تسجيل الدخول الخارجية."
    elif prediction == 5:
        category = "مشكلة في DHCP (DHCP Issue)"
        solution = "تحقق من نطاق عناوين IP المتاحة في إعدادات DHCP Server. تأكد من عدم وجود تضارب في العناوين (IP Conflict)."
    else:
        category = "مشكلة غير مصنفة"
        solution = "هذه المشكلة غير معروفة للنموذج الأولي. يرجى مراجعة سجلات MikroTik يدوياً."
        
    return {
        "message": message,
        "category": category,
        "solution": solution
    }

if __name__ == "__main__":
    # مثال على الاستخدام
    test_messages = [
        "critical: out of memory",
        "login failure for user admin from 1.2.3.4",
        "ether1 link is down",
        "client disconnected, reason: 4-way handshake timeout"
    ]
    
    print("\n--- اختبار نموذج الذكاء الاصطناعي ---")
    for msg in test_messages:
        result = analyze_log_message(msg)
        print(f"الرسالة: {result['message']}")
        print(f"التصنيف: {result['category']}")
        print(f"الحل المقترح: {result['solution']}\n")
