// بيانات الاتصال الثابتة (لغرض المحاكاة والاختبار)
// في التطبيق الحقيقي، سيتم جلب الـ ID من قاعدة البيانات بعد تسجيل الدخول
const MIKROTIK_CONNECTION_ID = 1; 
const BACKEND_URL = "https://mikrotik-hkcx.onrender.com";

// ----------------------------------------------------------------------
// دالة لجلب وعرض موارد النظام الحية (CPU, RAM, Uptime)
// ----------------------------------------------------------------------
async function fetchResources() {
    const statusCard = document.getElementById('connection-status');
    const statusText = document.getElementById('status-text');
    
    try {
        // محاكاة إنشاء اتصال MikroTik في قاعدة البيانات (للتجربة الأولى فقط)
        await createConnectionIfNotExist();
        
        const response = await fetch(`${BACKEND_URL}/connections/${MIKROTIK_CONNECTION_ID}/resources`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // تحديث حالة الاتصال
        statusCard.classList.remove('disconnected');
        statusCard.classList.add('connected');
        statusText.textContent = `متصل - ${data.board_name || 'MikroTik Router'}`;

        // تحديث مقاييس لوحة التحكم
        document.getElementById('cpu-load').textContent = `${data.cpu_load.toFixed(2)}%`;
        document.getElementById('free-memory').textContent = `${data.free_memory_mb.toFixed(2)} MiB`;
        document.getElementById('uptime').textContent = data.uptime;

    } catch (error) {
        console.error("Error fetching resources:", error);
        statusCard.classList.remove('connected');
        statusCard.classList.add('disconnected');
        statusText.textContent = `غير متصل - فشل الاتصال بالراوتر أو الخادم.`;
        
        // مسح البيانات القديمة
        document.getElementById('cpu-load').textContent = `--%`;
        document.getElementById('free-memory').textContent = `-- MiB`;
        document.getElementById('uptime').textContent = `--`;
    }
}

// ----------------------------------------------------------------------
// دالة لجلب وتحليل سجلات النظام
// ----------------------------------------------------------------------
async function fetchLogs() {
    const logsContainer = document.getElementById('logs-container');
    logsContainer.innerHTML = '<p>جاري سحب وتحليل السجلات...</p>';
    
    try {
        const response = await fetch(`${BACKEND_URL}/connections/${MIKROTIK_CONNECTION_ID}/logs`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const logs = await response.json();
        
        if (logs.length === 0) {
            logsContainer.innerHTML = '<p>لا توجد سجلات جديدة للتحليل.</p>';
            return;
        }
        
        logsContainer.innerHTML = ''; // مسح المحتوى القديم
        
        // عرض السجلات وتحليل الذكاء الاصطناعي
        logs.reverse().forEach(log => { // عرض الأحدث أولاً
            const logEntry = document.createElement('div');
            logEntry.className = 'log-entry';
            
            // رسالة السجل الأصلية
            const message = document.createElement('p');
            message.className = 'log-message';
            message.textContent = `[${log.timestamp}] (${log.topics}): ${log.message}`;
            logEntry.appendChild(message);
            
            // تحليل الذكاء الاصطناعي والحل المقترح
            const analysis = log.analysis;
            const analysisDiv = document.createElement('div');
            analysisDiv.className = 'log-analysis';
            analysisDiv.innerHTML = `
                <strong>تصنيف الذكاء الاصطناعي:</strong> ${analysis.category}<br>
                <strong>الحل المقترح:</strong> ${analysis.solution}
            `;
            logEntry.appendChild(analysisDiv);
            
            logsContainer.appendChild(logEntry);
        });

    } catch (error) {
        console.error("Error fetching logs:", error);
        logsContainer.innerHTML = `<p style="color: red;">فشل في جلب السجلات: ${error.message}</p>`;
    }
}

// ----------------------------------------------------------------------
// دالة مساعدة لمحاكاة إنشاء اتصال في قاعدة البيانات
// ----------------------------------------------------------------------
async function createConnectionIfNotExist() {
    // هذه الدالة تحاكي إنشاء اتصال في قاعدة البيانات لكي يعمل الـ API
    // في التطبيق الحقيقي، سيتم إنشاء هذا الاتصال عبر واجهة المستخدم
    const connectionData = {
        alias: "راوتر الاختبار",
        host: "192.168.88.1", // هذا الـ IP هو مجرد محاكاة
        port: 8728,
        username: "api_user",
        password: "secure_password"
    };

    try {
        // محاولة جلب الاتصال للتأكد من وجوده
        const checkResponse = await fetch(`${BACKEND_URL}/connections/${MIKROTIK_CONNECTION_ID}`);
        if (checkResponse.ok) {
            return; // الاتصال موجود بالفعل
        }
        
        // إذا لم يكن موجودًا، نقوم بإنشائه
        const createResponse = await fetch(`${BACKEND_URL}/connections/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(connectionData),
        });

        if (!createResponse.ok) {
            // إذا فشل الإنشاء (لأي سبب مثل فشل الاتصال بـ MikroTik الوهمي)
            console.warn("فشل محاكاة إنشاء الاتصال، قد يكون موجودًا بالفعل أو هناك مشكلة في الـ API.");
        }
        
    } catch (error) {
        console.error("Error in createConnectionIfNotExist:", error);
    }
}

// تشغيل الدوال عند تحميل الصفحة
window.onload = () => {
    fetchResources();
    // تحديث الموارد كل 30 ثانية
    setInterval(fetchResources, 30000); 
};
